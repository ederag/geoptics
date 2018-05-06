"""Test consistency between element and _G counterpart."""

import gc

from geoptics.guis.qt.debug import check_source_rays_consistency


def check_beam_consistency(beam):
	check_source_rays_consistency(beam)
	assert len(beam.rays) == beam.N_inter + 2


def test_source_beam_1(scene, source_beam_1):
	
	# check consistency before selection
	check_beam_consistency(source_beam_1)
	
	positions_before = [ray.parts[0].line.p.copy() for
	                    ray in source_beam_1.rays]
	dx = 10
	dy = 20
	# make sure the handles have been created
	source_beam_1.g.setSelected(True)
	
	# check consistency after selection
	check_beam_consistency(source_beam_1)
	
	# move bth handles
	source_beam_1.g.line_handles['start'].h_p0.moveBy(dx, dy)
	source_beam_1.g.line_handles['end'].h_p0.moveBy(dx, dy)
	for ray, position_before in zip(source_beam_1.rays, positions_before):
		# check ray starting point has been moved too
		position_after = ray.parts[0].line.p
		position_expected = position_before.copy().translate(dx=dx, dy=dy)
		print(position_before, position_after, position_expected)
		assert position_after == position_expected
	
	# make sure reference to ray is not kept,
	# otherwise it could not be deleted later on
	del ray
	
	# check consistency after move
	check_beam_consistency(source_beam_1)
	
	# this should trigger deletion of all rays but the two extremes
	# do not try source_beam_1.rays = []
	# which would leave N_inter to its previous value - not zero.
	source_beam_1.set(N_inter=0)
	assert len(source_beam_1.rays) == 2
	# make sure deletion occurs
	gc.collect()
	# check consistency after deletion
	check_beam_consistency(source_beam_1)
	
	source_beam_1.set(N_inter=2)
	assert len(source_beam_1.rays) == 4
	# check consistency after addition
	check_beam_consistency(source_beam_1)


def test_clear_scene(scene, region_polycurve_1, source_beam_1,
                     source_singleray_1):
	scene.clear()
	# there should be no items in scene.g
	gc.collect()
	assert not scene.g.items()
