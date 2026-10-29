extends SceneTree
func _init():
	var root = load("res://maps/nuketown/Nuketown.tscn").instantiate()
	get_root().add_child(root)
	var shots = [[Vector3(-45, 28, 40), Vector3(0, 12, -2), "aerial"], [Vector3(2, 14.0, 12), Vector3(0, 13, -2), "street"]]
	for s in shots:
		var cam = Camera3D.new(); cam.fov = 70; cam.far = 1500
		root.add_child(cam); await process_frame; cam.look_at_from_position(s[0], s[1]); cam.current = true
		for i in range(8): await process_frame
		var img = get_root().get_texture().get_image()
		img.save_png("/home/claude/work/out/shot_%s.png" % s[2])
		print("saved ", s[2], " ", img.get_size())
		cam.queue_free()
	quit(0)
