import urllib.request
import pickle

class PhD:
	def __init__(self, mgp, name=None, institution=None, year=None, dissertation=None, advisor=None):
		# Required parameters
		self.mgp = mgp					# MGP ID number; must be included
		
		# Optional parameters
		self.name = name				# Given name
		self.institution = institution			# Where the PhD was given
		self.year = year					# Year of issuance
		self.dissertation = dissertation		# Title of dissertation
		self.advisor = advisor				# Given as list with [name, mgp] in each component
		
	def __repr__(self):
		
		# String representation, formatted for human readability
		# Keep fields where we don't know information, but say so
		
		# Always have MGP ID and name
		s = f'MGP ID {self.mgp}\n{self.name}\n'
		
		if self.institution is None or len(self.institution) < 2:
			s += 'Institution: Unknown\n'
		else:
			s += f'Institution: {self.institution}\n'
			
		if self.year is None or len(self.year) < 2:
			s += 'Year: Unknown\n'
		else:
			s += f'Year: {self.year}\n'
			
		if self.dissertation is None or len(self.dissertation) < 2:
			s += 'Dissertation: Unknown\n'
		else:
			s += f'Dissertation: {self.dissertation}\n'
			
		# Handling multiple advisors
		if self.advisor is not None:
			if len(self.advisor) == 1:
				s += f'Advisor: {self.advisor[0].name}\n'
			else:
				for _ in range(len(self.advisor)):
					s += f'Advisor {_ + 1}: {self.advisor[_].name}\n'
		else:
			s += 'Unknown advisor\n'
		
		# Strip extra newline
		return s[:-1]
				
	def __eq__(self, other):
		# MGP ID is the only unique identifier
		return self.mgp == other.mgp
		
	def update(self):
		base = 'https://www.genealogy.math.ndsu.nodak.edu/id.php?id='
	
		# Open the MGP page and download the source code with UTF-8 encoding
		with urllib.request.urlopen(base+self.mgp) as page:
			lines = page.read().decode('utf-8').split('\n')

		# The first ~220 lines are just header information
		for line_index in range(200, len(lines)):
			line = lines[line_index]
		
			# ID is known. Student name is always in <h2> 
			if '/h2' in line:
				name = ' '.join([_ for _ in line.split('<')[0].split()])
		
			# This only appears in the line that has the institution and the four-digit year
			if 'margin-left: 0.5em' in line:
				institution = line.split('>')[1][:-6]
				year = line.split('>')[2][1:-6]
		
			# thesisTitle is an attribute
			if 'thesisTitle' in line:
				dissertation = lines[line_index + 2][:-13]
			
			# Save for later processing
			if 'Advisor' in line:
				advisor_line = line

		# At the base of the tree, the advisor is unknown
		if 'Unknown' not in advisor_line:
		
			# Strip the line down to just the parts that say "Advisor 1, Advisor 2, etc." 
			advisors = []
			advisor_raw_list =advisor_line.split('Advisor')[1:]
		
			# Loop over each advisor; append them as a PhD object that only
			# has the name and MGP ID number; update later as needed
		
			for advisor_raw in advisor_raw_list:
				adv_name = ' '.join([_ for _ in advisor_raw.split('>')[1][:-3].split()])
				adv_id = advisor_raw.split('=')[2].split('\"')[0]
				advisors.append(PhD(adv_id, adv_name))
	
		else:
			advisors = None
		
		# Fill in all the data and return		
		return PhD(self.mgp, name, institution, year, dissertation, advisors)

def generate_tree(root='238293'):
	# Have a starting person; defaults to me
	start = PhD(mgp=root).update()
	to_study = [start]			# These are the remaining names to look at
	ids_encountered = []			# This is a running list of who we've looked at
	family = []				# Save (as PhD objects) all the people we find

	# Save the data to a file
	filename = 'tree_for_id_'+root+'.txt'
	with open(filename, 'w+', encoding='utf-8') as f:
		
		while len(to_study) > 0:
			# Get the current person from the end of the list (following DFS)
			# Add them to the family and the IDs encountered
			current_person = to_study[-1]
			
			# Check if we already met this person
			if current_person.mgp in ids_encountered:
				to_study.remove(current_person)
				continue
				
			# Otherwise, we add them
			family.append(current_person)
			ids_encountered.append(current_person.mgp)
				
			# Write them to the file
			f.write(repr(current_person))
			f.write('\n\n')
		
			# Already studied them
			to_study.remove(current_person)
	
			# Now recurse
			parents = current_person.advisor
	
			try:
				# If we found an advisor, loop over them
				for p in parents:
					adv = p.update()
					
					if adv.mgp not in ids_encountered:
						to_study.append(adv)
				# If not, we were at the base already
			except:
				continue

	# Dump to a pickle object so we don't have to download everything again
	with open('pickle_for_id_'+root, 'wb') as f:
		pickle.dump(family, f)			
	
	# Return the family list
	return family
	
# Prompt user for input
if __name__ == '__main__':
	
	mgp = input("Enter an MGP ID Number: ")
	print('Generating tree')
	
	try:
		generate_tree(mgp)
		print(f'Tree saved at tree_for_id_{mgp}.txt')
	except:
		print('Unable to generate tree')
	print('Press enter to end')
	input()
