extends SceneTree
func _init():
	var scene_path = OS.get_environment("NK_SCENE")
	var out_path = OS.get_environment("NK_OUT")
	var root = load(scene_path).instantiate()
	get_root().add_child(root)
	var cam = Camera3D.new(); cam.fov = 75; cam.far = 3000
	root.add_child(cam); await process_frame; cam.current = true
	var views = [["spawnA", Vector3(-27, 14.3, -3), Vector3(0, 13, -2)], ["street", Vector3(2, 14.0, 12), Vector3(0, 13, -2)], ["aerial", Vector3(-45, 28, 40), Vector3(0, 12, -2)]]
	var cats = ["Terrain", "Mountains", "Structures", "Props", "Foliage", "Glass"]
	var res = {}
	for c in cats:
		for o in cats: root.get_node(o).visible = (o == c)
		for v in views:
			cam.look_at_from_position(v[1], v[2])
			for i in range(4): await process_frame
			res["%s/%s" % [c, v[0]]] = [int(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)), int(Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME))]
	var f = FileAccess.open(out_path, FileAccess.WRITE); f.store_string(JSON.stringify(res, "  ")); f.close()
	quit(0)
