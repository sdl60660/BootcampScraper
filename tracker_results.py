import tracking
from tracking import tracked_camp_changes
from tracking import tracking_groups

cats = ['locations', 'technologies']
groups = ['Java./NET', 'Top Camp', 'Selected Camp', 'Potential Markets']

for c in cats:
	for g in groups:
		print c
		print g
		print tracked_camp_changes(14, c, g)
		print