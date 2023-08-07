def test_translate_roundtrip(scene_polycurve_beam_singleray):
	assert len(scene_polycurve_beam_singleray.regions) > 0
	rp1 = scene_polycurve_beam_singleray.regions[0]
	cfg_orig = rp1.config
	dx = 10
	dy = 20
	rp1.translate(dx=dx, dy=dy)
	cfg_current = rp1.config
	assert cfg_orig != cfg_current
	rp1.translate(dx=-dx, dy=-dy)
	cfg_current = rp1.config
	assert cfg_orig == cfg_current


class TestConfig:
	def test_scene(self, scene):
		scene_config = scene.config
		assert 'Regions' in scene_config
		assert 'Sources' in scene_config
		
	def test_region(self, region):
		region_config = region.config
		assert 'Class' in region_config
		assert 'n' in region_config
	
	# to be called in test_source
	@classmethod
	def _test_ray(cls, ray):
		ray_config = ray.config
		assert 'parts' in ray_config
		assert len(ray_config['parts']) == len(ray.parts)
		for part in ray.parts:
			part_config = part.config
			assert 'line' in part_config
			assert 's' in part_config
	
	def test_source(self, source):
		source_config = source.config
		assert 'Class' in source_config
		assert len(source_config['rays']) == len(source.rays)
		# maybe testing all rays is a bit overkill,
		# but better catch inconsistencies between sources early
		for ray in source.rays:
			TestConfig._test_ray(ray)
