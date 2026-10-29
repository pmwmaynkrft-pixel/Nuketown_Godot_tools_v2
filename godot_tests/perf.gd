extends SceneTree
# قياس الأداء: draw calls / primitives / objects / video mem / FPS لعدة زوايا. البيئة: Xvfb + OpenGL برمجي (llvmpipe).
func _init():
	var scene_path = OS.get_environment("NK_SCENE")
	if scene_path == "": scene_path = "res://maps/nuketown/Nuketown.tscn"
	var out_path = OS.get_environment("NK_OUT")
	if out_path == "": out_path = "/tmp/perf.json"
	var root = load(scene_path).instantiate()
	get_root().add_child(root)
	var views = [
		["spawnA", Vector3(-27, 14.3, -3), Vector3(0, 13, -2)],
		["street", Vector3(2, 14.0, 12), Vector3(0, 13, -2)],
		["spawnB", Vector3(12, 14.3, -6), Vector3(-10, 13, -2)],
		["aerial", Vector3(-45, 28, 40), Vector3(0, 12, -2)],
		["wide_high", Vector3(0, 120, 160), Vector3(0, 10, 0)],
	]
	var cam = Camera3D.new(); cam.fov = 75; cam.far = 3000
	root.add_child(cam)
	await process_frame
	cam.current = true
	var results = {}
	for v in views:
		cam.look_at_from_position(v[1], v[2])
		for i in range(6): await process_frame
		var t0 = Time.get_ticks_usec(); var n = 20
		for i in range(n): await process_frame
		var dt = (Time.get_ticks_usec() - t0) / 1e6 / n
		results[v[0]] = {
			"draw_calls": Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME),
			"primitives": Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME),
			"objects": Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME),
			"frame_ms_software": snappedf(dt * 1000.0, 0.1),
		}
	results["video_mem_mb"] = snappedf(Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED) / 1048576.0, 0.1)
	results["texture_mem_mb"] = snappedf(Performance.get_monitor(Performance.RENDER_TEXTURE_MEM_USED) / 1048576.0, 0.1)
	results["buffer_mem_mb"] = snappedf(Performance.get_monitor(Performance.RENDER_BUFFER_MEM_USED) / 1048576.0, 0.1)
	results["static_mem_mb"] = snappedf(Performance.get_monitor(Performance.MEMORY_STATIC) / 1048576.0, 0.1)
	results["nodes"] = int(Performance.get_monitor(Performance.OBJECT_NODE_COUNT))
	var f = FileAccess.open(out_path, FileAccess.WRITE); f.store_string(JSON.stringify(results, "  ")); f.close()
	print("PERF_DONE ", out_path)
	quit(0)
