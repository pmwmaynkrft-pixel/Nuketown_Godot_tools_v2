extends SceneTree
func _init():
	var root = load("res://maps/nuketown/Nuketown.tscn").instantiate()
	get_root().add_child(root)
	await physics_frame
	await physics_frame
	var space = root.get_world_3d().direct_space_state
	var cap = CapsuleShape3D.new(); cap.radius = 0.4; cap.height = 1.8
	var f = FileAccess.open("/home/claude/work/out/spots.txt", FileAccess.WRITE)
	for zi in range(-60, 61, 3):
		var line = ""
		for xi in range(-60, 61, 3):
			var ch = "."
			var p = Vector3(xi, 22, zi)
			var r = space.intersect_ray(PhysicsRayQueryParameters3D.create(p, p + Vector3(0,-40,0)))
			if r:
				var y = r.position.y
				if r.normal.y > 0.9 and y > 11.3 and y < 14.8:
					var q = PhysicsShapeQueryParameters3D.new()
					q.shape = cap; q.transform = Transform3D(Basis(), Vector3(xi, y + 1.0, zi)); q.margin = 0.05
					var hit = space.intersect_shape(q, 1)
					# headroom: ray up 3m
					var up = space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(xi, y+1.95, zi), Vector3(xi, y+4.5, zi)))
					if hit.size() == 0:
						ch = "o" if up else "+"
						f.store_line("SPOT %d %.2f %d %s" % [xi, y, zi, "indoor" if up else "open"])
					else: ch = "x"
				else: ch = "#"
			line += ch
		f.store_line("ROW z=%d %s" % [zi, line])
	f.close()
	quit(0)
