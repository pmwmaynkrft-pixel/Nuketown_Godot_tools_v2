extends SceneTree
func _init():
	var ps: PackedScene = load("res://maps/nuketown/Nuketown.tscn")
	if ps == null:
		print("FAIL: load returned null"); quit(1); return
	var root = ps.instantiate()
	get_root().add_child(root)
	var n_nodes := 0; var n_mesh := 0; var n_body := 0; var n_shape := 0; var tris := 0
	var stack = [root]
	while stack.size() > 0:
		var n = stack.pop_back(); n_nodes += 1
		if n is MeshInstance3D:
			n_mesh += 1
			if n.mesh: 
				for s in range(n.mesh.get_surface_count()):
					var a = n.mesh.surface_get_arrays(s)
					if a[Mesh.ARRAY_INDEX] != null: tris += a[Mesh.ARRAY_INDEX].size()/3
		if n is StaticBody3D: n_body += 1
		if n is CollisionShape3D and n.shape is ConcavePolygonShape3D: n_shape += 1
		for c in n.get_children(): stack.append(c)
	print("nodes=", n_nodes, " meshinstances=", n_mesh, " staticbodies=", n_body, " concave_shapes=", n_shape, " mesh_tris=", tris)
	await physics_frame
	await physics_frame
	var space = root.get_world_3d().direct_space_state
	for p in [Vector3(-25,60,-8), Vector3(18,60,-3), Vector3(0,60,0), Vector3(-3,60,8)]:
		var q = PhysicsRayQueryParameters3D.create(p, p + Vector3(0,-120,0))
		var r = space.intersect_ray(q)
		print("ray ", p, " -> ", (r.position if r else "NO HIT"))
	quit(0)
