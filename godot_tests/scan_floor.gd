extends SceneTree
func _init():
	var root = load("res://maps/nuketown/Nuketown.tscn").instantiate()
	get_root().add_child(root)
	await physics_frame
	await physics_frame
	var space = root.get_world_3d().direct_space_state
	var f = FileAccess.open("/home/claude/work/out/floor.csv", FileAccess.WRITE)
	for zi in range(-80, 81, 2):
		var row = []
		for xi in range(-90, 71, 2):
			var p = Vector3(xi, 40, zi)
			var r = space.intersect_ray(PhysicsRayQueryParameters3D.create(p, p + Vector3(0,-80,0)))
			row.append("%.2f" % (r.position.y if r else -99.0))
		f.store_line(",".join(row))
	f.close()
	quit(0)
