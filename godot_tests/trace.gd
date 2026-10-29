extends SceneTree
func _init():
	var root = load("res://maps/nuketown/Nuketown.tscn").instantiate()
	get_root().add_child(root)
	await physics_frame
	await physics_frame
	var space = root.get_world_3d().direct_space_state
	# static trace: floor height every 1m along +x from SpawnA4 (-30,-3)
	var a4 = root.get_node("SpawnPoints/TeamA/SpawnA4").global_position
	var out = ""
	for i in range(0, 30):
		var p = Vector3(a4.x + i, a4.y + 3.0, a4.z)
		var r = space.intersect_ray(PhysicsRayQueryParameters3D.create(p, p + Vector3(0,-40,0)))
		out += "%d:%s " % [i, ("%.1f" % r.position.y) if r else "NONE"]
	print("A4 +x floor line: ", out)
	var a1 = root.get_node("SpawnPoints/TeamA/SpawnA1").global_position
	out = ""
	for i in range(0, 30):
		var p = Vector3(a1.x - i, a1.y + 3.0, a1.z)
		var r = space.intersect_ray(PhysicsRayQueryParameters3D.create(p, p + Vector3(0,-40,0)))
		out += "%d:%s " % [i, ("%.1f" % r.position.y) if r else "NONE"]
	print("A1 -x floor line: ", out)
	quit(0)
