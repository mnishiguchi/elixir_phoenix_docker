# smoke_app の生成後、Livebook イメージ内で実行します（smoke_livebook.py を参照）。
{:ok, ip} = :inet.getaddr(~c"livebook", :inet)
{:ok, _} = Node.start(String.to_atom("starter_smoke@#{:inet.ntoa(ip)}"), :longnames)
{:ok, _} = DynamicSupervisor.start_link(strategy: :one_for_one, name: Livebook.RuntimeSupervisor)

["attached", node_name, cookie] =
  String.split(System.fetch_env!("LIVEBOOK_DEFAULT_RUNTIME"), ":", parts: 3)

runtime = Livebook.Runtime.Attached.new(String.to_atom(node_name), String.to_atom(cookie))
connector = Livebook.Runtime.connect(runtime)

receive do
  {:runtime_connect_done, ^connector, {:ok, connected}} ->
    try do
      Livebook.Runtime.take_ownership(connected, [])
      ref = make_ref()
      # Phoenix ノード上で評価が実行され、そのデータベースを利用できることを確認します。
      code = """
      true = Node.self() == :"phoenix@web.phoenix.test"
      [[1]] = SmokeApp.Repo.query!("SELECT 1").rows
      :starter_smoke_ok
      """
      Livebook.Runtime.evaluate_code(connected, :elixir, code, {:smoke, ref}, [], [])

      receive do
        {:runtime_evaluation_response, ^ref, output, metadata} ->
          unless metadata.errored == false and output.type == :terminal_text and
                   String.contains?(output.text, "starter_smoke_ok") do
            raise "Attached evaluation failed"
          end
          IO.puts("Livebook attached evaluation and Phoenix database query passed")
      after
        30_000 -> raise "Attached evaluation timed out"
      end
    after
      Livebook.Runtime.disconnect(connected)
    end

  {:runtime_connect_done, ^connector, {:error, error}} ->
    raise "Attached connection failed: #{error}"
after
  30_000 -> raise "Attached connection timed out"
end
