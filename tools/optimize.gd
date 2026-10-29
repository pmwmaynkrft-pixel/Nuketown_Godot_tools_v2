@tool
extends SceneTree
# مرحلة تحسين الأداء: يقرأ Nuketown_original.tscn ويكتب Nuketown.tscn محسّنًا.
# - مواد مشتركة (materials/*.tres) بدل نسخة لكل نموذج
# - مجسمات فريدة (meshes/*.res) بحسب بصمة الهندسة
# - MultiMeshInstance3D للعناصر المتكررة داخل خلية 64م
# - دمج المجسمات الفردية داخل الخلية (مع الحفاظ على المواد)
# - visibility_range حسب حجم العنصر (للأدوات والنباتات والزجاج فقط)
const SRC := "res://maps/nuketown/Nuketown_original.tscn"
const DST := "res://maps/nuketown/Nuketown.tscn"
const CELL := 64.0
const TERRAIN_CELL := 256.0
const CELL_SMALL := 32.0
const HEAVY_TRIS := 3000
const HEAVY_RANGE := 70.0
const MM_MIN := 3
const RANGE_TINY := 45.0
const RANGE_SMALL := 80.0
const RANGE_MED := 140.0
const RANGE_GLASS := 150.0

var mat_cache := {}      # key -> Material
var mesh_cache := {}     # sig -> Mesh (unique, saved)
var src_mesh_cache := {} # model -> ArrayMesh
var sigs := {}
var stats := {"materials": 0, "unique_meshes": 0, "multimeshes": 0, "merged_nodes": 0, "single_nodes": 0, "mm_instances": 0, "merged_entities": 0}

func shared_mat(m: Material) -> Material:
	var sm := m as StandardMaterial3D
	var tex_path := ""
	if sm and sm.albedo_texture: tex_path = sm.albedo_texture.resource_path
	var key := "%s|%d|%d|%s|%.2f" % [tex_path, sm.transparency if sm else 0, sm.cull_mode if sm else 0, str(sm.albedo_color) if sm else "", sm.alpha_scissor_threshold if sm else 0.0]
	if mat_cache.has(key): return mat_cache[key]
	var nm := m.duplicate() as Material
	var path := "res://maps/nuketown/materials/m_%03d.tres" % mat_cache.size()
	ResourceSaver.save(nm, path)
	var loaded := load(path) as Material
	mat_cache[key] = loaded; stats.materials += 1
	return loaded

func get_src_mesh(model: String, inst: Node) -> ArrayMesh:
	if src_mesh_cache.has(model): return src_mesh_cache[model]
	var mis := inst.find_children("*", "MeshInstance3D", true, false)
	var mesh: ArrayMesh = null
	if mis.size() > 0: mesh = (mis[0] as MeshInstance3D).mesh as ArrayMesh
	src_mesh_cache[model] = mesh
	return mesh

func unique_mesh(sig: String, src: ArrayMesh) -> Mesh:
	if mesh_cache.has(sig): return mesh_cache[sig]
	var m := src.duplicate() as ArrayMesh
	for i in range(m.get_surface_count()):
		m.surface_set_material(i, shared_mat(src.surface_get_material(i)))
	var path := "res://maps/nuketown/meshes/%s.res" % sig
	ResourceSaver.save(m, path)
	var loaded := load(path) as Mesh
	mesh_cache[sig] = loaded; stats.unique_meshes += 1
	return loaded

var tri_cache := {}
func tri_count(sig: String, m: ArrayMesh) -> int:
	if tri_cache.has(sig): return tri_cache[sig]
	var t := 0
	for i in range(m.get_surface_count()):
		t += (m.surface_get_arrays(i)[Mesh.ARRAY_INDEX] as PackedInt32Array).size() / 3
	tri_cache[sig] = t
	return t

func cell_size(c: String) -> float:
	if c == "Terrain": return TERRAIN_CELL
	if c == "Structures": return CELL
	return CELL_SMALL

func size_class(sz: float) -> int:
	if sz < 0.6: return 0
	if sz < 1.5: return 1
	if sz < 3.5: return 2
	return 3

func range_for(cat: String, sc: int, heavy: int) -> float:
	if cat == "Glass": return RANGE_GLASS
	if cat == "Props" or cat == "Foliage":
		var r: float = [RANGE_TINY, RANGE_SMALL, RANGE_MED, 0.0][sc]
		if heavy == 1 and sc < 3: r = minf(r, HEAVY_RANGE)
		return r
	return 0.0

func _init():
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://maps/nuketown/materials"))
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://maps/nuketown/meshes"))
	var jf := FileAccess.open("res://maps/nuketown/_meta/geom_sig.json", FileAccess.READ)
	sigs = JSON.parse_string(jf.get_as_text())
	var root: Node = (load(SRC) as PackedScene).instantiate()
	var cats := ["Terrain", "Mountains", "Structures", "Props", "Foliage", "Glass"]
	var before_nodes := 0
	for c in cats:
		var g: Node3D = root.get_node(c)
		var ents := g.get_children()
		before_nodes += ents.size()
		# تجميع
		var groups := {}   # key "cell|sc" -> { sig -> [xf...] }, plus meta
		var singles_out: Array = []
		for e in ents:
			var model: String = e.scene_file_path.get_file().get_basename()
			var src := get_src_mesh(model, e)
			if src == null: continue
			var sig: String = sigs.get(model, model)
			var xf: Transform3D = e.transform
			if c == "Mountains":
				singles_out.append([sig, src, xf])
				continue
			var longest := src.get_aabb().get_longest_axis_size() * xf.basis.get_scale().x
			var sc := size_class(longest)
			var csz := cell_size(c)
			if c == "Terrain": sc = 0
			var cell := Vector2i(floori(xf.origin.x / csz), floori(xf.origin.z / csz))
			var heavy := 1 if tri_count(sig, src) > HEAVY_TRIS else 0
			var key := "%d,%d|%d|%d" % [cell.x, cell.y, sc, heavy]
			if not groups.has(key): groups[key] = {"cell": cell, "sc": sc, "heavy": heavy, "by_sig": {}, "src": {}}
			var gd = groups[key]
			if not gd.by_sig.has(sig): gd.by_sig[sig] = []; gd.src[sig] = src
			gd.by_sig[sig].append(xf)
		# إزالة العقد الأصلية
		for e in ents:
			g.remove_child(e); e.free()
		# Terrain/Mountains: MeshInstance3D لكل كيان (هندسة فريدة)
		for s in singles_out:
			var mi := MeshInstance3D.new()
			mi.mesh = unique_mesh(s[0], s[1]); mi.transform = s[2]
			mi.name = "%s_%d" % [c, stats.single_nodes]
			mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			g.add_child(mi); mi.owner = root; stats.single_nodes += 1
		# باقي الفئات
		for key in groups:
			var gd = groups[key]
			var cell: Vector2i = gd.cell
			var csz2 := cell_size(c)
			var center := Vector3((cell.x + 0.5) * csz2, 0.0, (cell.y + 0.5) * csz2)
			var rng := range_for(c, gd.sc, gd.heavy)
			var leftovers := []   # [sig, src, xf]
			for sig in gd.by_sig:
				var xfs: Array = gd.by_sig[sig]
				if xfs.size() >= MM_MIN and c != "Terrain":
					var mm := MultiMesh.new()
					mm.transform_format = MultiMesh.TRANSFORM_3D
					mm.mesh = unique_mesh(sig, gd.src[sig])
					mm.instance_count = xfs.size()
					for i in range(xfs.size()):
						var t: Transform3D = xfs[i]; t.origin -= center
						mm.set_instance_transform(i, t)
					var mmi := MultiMeshInstance3D.new()
					mmi.multimesh = mm; mmi.position = center
					mmi.name = "MM_%s_%d_%d_%d_%d" % [sig.substr(0, 6), cell.x, cell.y, gd.sc, gd.heavy]
					mmi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
					if rng > 0.0: mmi.visibility_range_end = rng
					g.add_child(mmi); mmi.owner = root
					stats.multimeshes += 1; stats.mm_instances += xfs.size()
				else:
					for xf in xfs: leftovers.append([sig, gd.src[sig], xf])
			if leftovers.size() == 0: continue
			# دمج المتبقي في مجسم واحد بسطح لكل مادة
			var surf := {}   # matkey -> {mat, v, n, uv, idx}
			for lo in leftovers:
				var src: ArrayMesh = lo[1]; var xf: Transform3D = lo[2]
				var rot := Transform3D(xf.basis.orthonormalized(), Vector3.ZERO)
				var scl := xf.basis.get_scale().x
				var rel := xf; rel.origin -= center
				for si in range(src.get_surface_count()):
					var mat := shared_mat(src.surface_get_material(si))
					var k := mat.resource_path
					if not surf.has(k): surf[k] = {"mat": mat, "v": PackedVector3Array(), "n": PackedVector3Array(), "uv": PackedVector2Array(), "idx": PackedInt32Array()}
					var d = surf[k]
					var arr := src.surface_get_arrays(si)
					var verts: PackedVector3Array = arr[Mesh.ARRAY_VERTEX]
					var off: int = d.v.size()
					d.v.append_array(rel * verts)
					if arr[Mesh.ARRAY_NORMAL] != null: d.n.append_array(rot * (arr[Mesh.ARRAY_NORMAL] as PackedVector3Array))
					else:
						var z := PackedVector3Array(); z.resize(verts.size()); d.n.append_array(z)
					if arr[Mesh.ARRAY_TEX_UV] != null: d.uv.append_array(arr[Mesh.ARRAY_TEX_UV])
					else:
						var z2 := PackedVector2Array(); z2.resize(verts.size()); d.uv.append_array(z2)
					var idx: PackedInt32Array = arr[Mesh.ARRAY_INDEX]
					var base: int = d.idx.size()
					d.idx.resize(base + idx.size())
					for q in range(idx.size()): d.idx[base + q] = idx[q] + off
			var use_lod: bool = (c == "Props" or c == "Foliage" or c == "Terrain")
			var out_mesh: Mesh
			if use_lod:
				var im := ImporterMesh.new()
				for k in surf:
					var d = surf[k]; var a := []; a.resize(Mesh.ARRAY_MAX)
					a[Mesh.ARRAY_VERTEX] = d.v; a[Mesh.ARRAY_NORMAL] = d.n; a[Mesh.ARRAY_TEX_UV] = d.uv; a[Mesh.ARRAY_INDEX] = d.idx
					im.add_surface(Mesh.PRIMITIVE_TRIANGLES, a, [], {}, d.mat)
				im.generate_lods(25.0, 60.0, [])
				out_mesh = im.get_mesh()
			else:
				var am := ArrayMesh.new()
				for k in surf:
					var d = surf[k]; var a := []; a.resize(Mesh.ARRAY_MAX)
					a[Mesh.ARRAY_VERTEX] = d.v; a[Mesh.ARRAY_NORMAL] = d.n; a[Mesh.ARRAY_TEX_UV] = d.uv; a[Mesh.ARRAY_INDEX] = d.idx
					am.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, a)
					am.surface_set_material(am.get_surface_count() - 1, d.mat)
				out_mesh = am
			var mpath := "res://maps/nuketown/meshes/merged_%s_%d_%d_%d_%d.res" % [c, cell.x, cell.y, gd.sc, gd.heavy]
			ResourceSaver.save(out_mesh, mpath)
			var mi := MeshInstance3D.new()
			mi.mesh = load(mpath) as Mesh; mi.position = center
			mi.name = "Merged_%d_%d_%d_%d" % [cell.x, cell.y, gd.sc, gd.heavy]
			mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			if rng > 0.0: mi.visibility_range_end = rng
			g.add_child(mi); mi.owner = root
			stats.merged_nodes += 1; stats.merged_entities += leftovers.size()
		print("category ", c, " done, original entities ", ents.size(), " nodes now ", g.get_child_count())
	var ps := PackedScene.new()
	print("pack: ", ps.pack(root))
	print("save: ", ResourceSaver.save(ps, DST))
	print("OPT_STATS ", JSON.stringify(stats))
	quit(0)
