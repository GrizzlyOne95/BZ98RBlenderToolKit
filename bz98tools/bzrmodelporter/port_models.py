# Battlezone 98R Blender ToolKit
# Copyright (C) 2024–2025 “GrizzlyOne95” and contributors
# 
# This file is part of BZ98R Blender ToolKit, which is distributed
# under the terms of the GNU General Public License v3.0.
# See the LICENSE file or <https://www.gnu.org/licenses/>.

import sys
import os
import traceback
import argparse
from argparse import ArgumentParser
from configparser import ConfigParser
from pathlib import Path

# Use relative imports inside the bz98tools.bzrmodelporter package
from .bzportmodels import (port_bwd2, port_geo, port_map)
from .spacial import Transform



import re
def portconfig_from_odf(odf_path):
	class_label = None
	base_name = None
	nation = None
	
	RE_HEADER = re.compile(r"^\s*\[(.+?)\]")
	RE_KVP = re.compile(r"^\s*(\S+?)\s*=\s*(.*?)\s*$")
	with open(odf_path, 'rt') as stream:
		cur_header = None
		for line in stream.readlines():
			m = RE_HEADER.match(line)
			if(m is not None):
				cur_header, = m.groups()
				continue
			if(cur_header != "GameObjectClass"):
				continue
			m = RE_KVP.match(line)
			if(m is not None):
				key, value = m.groups()
				if(key.lower() == "classlabel"):
					class_label = value
				elif(key.lower() == "basename"):
					base_name = value
				elif(key.lower() == "nation"):
					nation = value
				continue
	
	if(class_label is not None):
		class_label = class_label.strip().strip("\"'")
	else:
		raise Exception("No classLabel in [GameObjectClass]")
	
	if(base_name is not None):
		base_name = base_name.strip().strip("\"'")
	else:
		base_name = odf_path.stem

	if(nation is not None):
		nation = nation.strip().strip("\"'")
	else:
		nation = odf_path.stem[0]
	
	return class_label, base_name, nation
		
def is_vehicle_type(class_label):
	return class_label in {
		'apc', 'hover', 'howitzer', 'minelayer', 'sav', 'scavenger', 'tug', 'turrettank', 'walker', 'wingman',
		'armory', 'constructionrig', 'factory', 'producer', 'recycler', 'turret', 
		'person',
		'ammopack', 'camerapod', 'daywrecker', 'powerup', 'repairkit', 'dropoff', 'torpedo', 'wpnpower',
	}
		
def is_building_type(class_label):
	return class_label in {
		'animbuilding', 'artifact', 'barracks', 'commtower', 'geyser', 'i76building', 'portal', 'powerplant', 'repairdepot', 'scrapfield', 'scrapsilo', 'shieldtower', 'supplydepot',
		'i76building2',
		'flare', 'i76sign', 'magnet', 'proximity', 'spawnpnt', 'spraybomb', 'weaponmine',
		'scrap',
	}

class AssetResolver():
	def __init__(self, input_dirpath, dest_dirpath, resource_dir_list, act_path):
		self.input_dirpath = input_dirpath         # Path to the directory of the given file to port
		self.dest_dirpath = dest_dirpath           # Path to the destination directory to place the new files
		self.resource_dir_list = resource_dir_list # List of directories to search for resources after the input file directory
		self.overwrite_textures = True # If any of these are False
		self.overwrite_material = True #   then the corresponding files
		self.overwrite_mesh = True     #   will not be overwritten if
		self.overwrite_skeleton = True #   they already exist.
		
		self.walk_directory_tree = True
		
		# TODO: Pull from a config file
		self.act_path = act_path
	
	def get_resource_path(self, basename):
		if(self.walk_directory_tree):
			for dirpath, dirlist, filelist in os.walk(self.input_dirpath):
				filepath = Path(dirpath, basename)
				if(filepath.exists()):
					return filepath
		else:
			filepath = Path(self.input_dirpath, basename)
			if(filepath.exists()):
				return filepath
		
		for resource_dir in self.resource_dir_list:
			filepath = Path(resource_dir , basename)
			if(filepath.exists()):
				return filepath
		print(f"Could not find {basename}")
		return None
	
	def get_vdf_path(self, name):
		return self.get_resource_path(name+".vdf")
	
	def get_sdf_path(self, name):
		return self.get_resource_path(name+".sdf")
	
	def get_act_path(self):
		# .act files are color palette files needed to port .map textures files using the indexed color format.
		# The texture files don't specify a specific .act file, instead they're specified in the .trn.
		# Because of this, all textures using the indexed color format are 
		#   expected to look correct with any of the standard world .act files.
		return self.act_path
	
	def get_geo_path(self, name):
		# .geo files contain mesh geometry data and are referenced in bwd2 (vdf/sdf) files by name, but not path.
		return self.get_resource_path(name+".geo")
		
	def get_map_path(self, name):
		# .map files are textures files.
		return self.get_resource_path(name+".map")
		
	def get_output_texture_path(self, name):
		# Destination for .dds texture files ported from .map textures.
		path = self.dest_dirpath / name
		if(not self.overwrite_textures and path.exists()):
			return None
		return path
		
	def get_output_material_path(self, name):
		# Destination for the OGRE .material file.
		path = self.dest_dirpath / name
		if(not self.overwrite_material and path.exists()):
			return None
		return path
	
	def get_output_mesh_path(self, name):
		# Destination for an OGRE .mesh file.
		path = self.dest_dirpath / name
		if(not self.overwrite_mesh and path.exists()):
			return None
		return path
		
	def get_output_skeleton_path(self, name):
		# Destination for an OGRE .skeleton file.
		path = self.dest_dirpath / name
		if(not self.overwrite_skeleton and path.exists()):
			return None
		return path

class ScopeScreen:
	def __init__(self, x, y, z, scale, behind_dist):
		self.x = x
		self.y = y
		self.z = z
		self.scale = scale
		self.behind_dist = behind_dist
	
	def __iter__(self):
		return iter((self.x, self.y, self.z, self.scale, self.behind_dist))
		

class ScopeSettings:
	def __init__(self,
		scope=None,
		type='AUTO',
		nation=None,
		screen=None,
		gun_name=None,
		transform=None,
		texture=None,
	):
		self.scope = scope
		self.type = type
		self.nation = nation
		self.screen = screen
		self.gun_name = gun_name
		self.transform = transform if transform is not None else Transform()
		self.texture = texture
	
	def scope_enabled(self):
		return self.scope is True
	
	def scope_disabled(self):
		return self.scope is False
	
	def scope_auto(self):
		return self.scope is None
	
	def type_auto(self):
		return self.type == 'AUTO'
	
	def type_fixed(self):
		return self.type == 'FIXED'
	
	def type_attached(self):
		return self.type == 'ATTACHED'
	
	def type_geometry(self):
		return self.type == 'GEOMETRY'
	
	def position_american(self):
		if(self.nation is None):
			return False
		if(self.screen is not None):
			return False
		return self.nation[0] != 's'
	
	def position_soviet(self):
		if(self.nation is None):
			return False
		if(self.screen is not None):
			return False
		return self.nation[0] == 's'
	
	def position_auto(self):
		return self.nation is None and self.screen is None
	
	def fixed_transform(self):
		return self.screen

class BoundingBoxScaleFactors:
	def __init__(self, x=1.0, y=1.0, z=1.0):
		self.x = x
		self.y = y
		self.z = z
	
	
class SettingsController:
	def __init__(self,
		name="model",
		suffix="",
		headlights=False,   # Boolean
		person=None,        # TERNARY_OPTIONS
		turret=None,        # TERNARY_OPTIONS
		cockpit=None,       # TERNARY_OPTIONS
		skeletalanims=None, # TERNARY_OPTIONS
		scope=None,         # ScopeSettings
		no_pov_rots=False,  # Boolean
		flat_colors=False,  # Boolean
		boundingbox_scale_factors=None,
		nowrite=False,      # Boolean
		verbose=False,      # Boolean
	):
		self.name = name
		self.suffix = suffix
		self.headlights = headlights
		self.person = person
		self.turret = turret
		self.cockpit = cockpit
		self.skeletalanims = skeletalanims
		self.scope = scope or ScopeSettings()
		self.no_pov_rots = no_pov_rots
		self.flat_colors = flat_colors
		self.boundingbox_scale_factors = boundingbox_scale_factors
		self.nowrite = nowrite
		self.verbose = verbose
	
	def get_model_name(self):
		return self.name
	
	def get_material_suffix(self):
		return self.suffix
	
	def headlights_enabled(self):
		return self.headlights
	
	def separate_cockpit_enabled(self):
		return self.cockpit is True
	def separate_cockpit_disabled(self):
		return self.cockpit is False
	def separate_cockpit_auto(self):
		return self.cockpit is None
	
	def person_enabled(self):
		return self.person is True
	def person_disabled(self):
		return self.person is False
	def person_auto(self):
		return self.person is None
	
	def turret_enabled(self):
		return self.turret is True
	def turret_disabled(self):
		return self.turret is False
	def turret_auto(self):
		return self.turret is None
	
	def person_anims_enabled(self):
		return self.skeletalanims is True
	def person_anims_disabled(self):
		return self.skeletalanims is False
	def person_anims_auto(self):
		return self.skeletalanims is None
	
	def pov_movement_anim_rotations_disabled(self):
		return self.no_pov_rots
	
	def only_flat_colors_enabled(self):
		return self.flat_colors
	
	def suppress_write(self): 
		return self.nowrite
	
	def verbose_log(self):
		return self.verbose
	
def parse_args():
	ternary_choices = ['Auto', 'True', 'False']
	def ternary(s):
		s = s.upper()
		if(s == 'TRUE'):
			return True
		elif(s == 'FALSE'):
			return False
		elif(s == 'AUTO'):
			return None
		else:
			raise ValueError("Ternary option must be either 'True', 'False', or 'Auto'; Got '{s}'")
	
	ap = ArgumentParser(
	formatter_class=argparse.RawDescriptionHelpFormatter,
	epilog='''
Add a file 'config.cfg' in the same directory as this script to specify default files/search locations, or use the --config argument to point to a different config file.\n
\n
The first line of the config file should be a filepath to an .act color palette used for porting indexed images. Every line after that should be directory paths that will be used as default search locations for game assets. Note the directory of the target file will always be searched first before these paths.
''')
	ap.add_argument("--name",
		action='store', 
		help="Name to give the final model files",
	)
	ap.add_argument("--suffix",
		action='store', default="_port",
		help="Suffix appended to material file names",
	)
	ap.add_argument("--headlights",
		action='store_true',
		help="Enable the automatic creation of headlights",
	)
	ap.add_argument("--person",
		action='store', default='Auto',
		choices=ternary_choices,
		help="Force this object to be flagged as a person",
	)
	ap.add_argument("--turret",
		action='store', default='Auto',
		choices=ternary_choices,
		help="Force this object to be flagged as a turret",
	)
	ap.add_argument("--cockpit",
		action='store', default='Auto',
		choices=ternary_choices,
		help="Force the creation or suppression of separate cockpit model files. When disabled, both the external and cockpit geometry are put into a single mesh and skeleton file, but the cockpit cannot animate.",
	)
	ap.add_argument("--skeletalanims",
		action='store', default='Auto',
		choices=ternary_choices,
		help="Force the creation or suppression of skeletal person animations",
	)
	ap.add_argument("--scope",
		action='store', default='Auto',
		choices=ternary_choices,
		help="Force the creation or suppression of a person sniper scope",
	)
	ap.add_argument("--scopetype",
		action='store', default='AUTO', type=str.upper,
		choices=['AUTO', 'FIXED', 'ATTACHED', 'GEOMETRY'],
		help="If a sniper scope is created: Specifies whether the scope is a square fixed on screen (classic style, turns on/off upon crouch/uncrouch), a square attached to the gun model (Redux style, always on), or textured directly on the geometry (Redux style, geos with special scope texture use scope material, always on). Auto picks between FIXED and GEOMETRY depending on the presence of the special scope texture.",
	)
	ap.add_argument("--scopenation",
		action='store', default=None,
		help="If using the FIXED scope: Nation string determines where the scope appears on screen. A nation string starting with 's' uses default Soviet placement,  while any other string uses default American placement.",
	)
	ap.add_argument("--scopescreen",
		action='store', nargs=5, type=float,
		metavar=("X", "Y", "Z", "SCALE", "BEHIND_DIST"),
		help="If using the FIXED scope: Overrides default values from the nation. Camera-relative position of the sniper scope X, Y, and Z, size of scope SIZE, and distance behind the camera to hide the scope when disabled BEHIND_DIST.",
	)
	ap.add_argument("--scopegun",
		action='store',
		help="If using the ATTACHED scope: Name of the gun geo to attach the scope to.",
	)
	ap.add_argument("--scopetransform",
		action='store', nargs=12, type=float,
		metavar=("RX", "RY", "RZ", "UX", "UY", "UZ", "FX", "FY", "FZ", "PX", "PY", "PZ"),
		help="If using the ATTACHED scope: Gun-relative transform of the sniper scope. Right, up, front, and position vectors.",
	)
	ap.add_argument("--scopetexture",
		action='store', default='__scope',
		help="If using the GEOMETRY scope: Name of the texture that will be replaced with the scope material. A .map file of this name doesn't need to exist, and will be ignored if it does. Defaults to '__scope'.",
	)
	ap.add_argument("--nopovrots",
		action='store_true',
		help="If using skeletal person animations: All rotation keyframes for the POV are removed from the four directional movement animations only.",
	)
	ap.add_argument("--flatcolors",
		action='store_true',
		help="Force the use of flat per-face color texturing.",
	)
	ap.add_argument("--boundsmult",
		action='store', nargs=3, type=float,
		metavar=("X", "Y", "Z"),
		help="Scale factors for the mesh bounds.",
	)
	ap.add_argument("--act",
		action='store', type=Path, default=None,
		help="Name of an .act color palette file used to port .map texture files that use the indexed color format",
	)
	ap.add_argument("--config",
		action='store', type=Path, default=None,
		help="Name of a configuration file for defining default paths for this model porting utility",
	)
	ap.add_argument("--onlyonce",
		action='store_true',
		help="Don't port files when the mesh is already in the target directory",
	)
	ap.add_argument("--nowrite",
		action='store_true',
		help="Suppress file writing (for testing)",
	)
	#ap.add_argument("--verbose",  # TODO: Allow verbosity to be changed meaningfully!
	#	action='store_true',
	#	help="Enable verbose logging",
	#)
	ap.add_argument("--dest",
		action='store', type=Path, default=None,
		help="destination directory to write files into",
	)
	ap.add_argument("filepaths",
		nargs='+', type=Path,
		metavar="file",
		help="Path to the file or files you want to port. Allowed filetypes are .vfd, .sdf, .geo, and .map files.",
	)
	args = ap.parse_args()
	args.person = ternary(args.person)
	args.turret = ternary(args.turret)
	args.cockpit = ternary(args.cockpit)
	args.skeletalanims = ternary(args.skeletalanims)
	args.scope = ternary(args.scope)
	
	return args



# TODO: Turret fix!
# TODO: Make sure file extensions aren't case sensitive!
if(__name__=='__main__'):
	script_path = Path(sys.argv[0])
	resource_dir_list = []
	
	args = parse_args()
	config_path = args.config or (script_path.parent / "config.cfg")
	
	# TODO: argument to specify the config file
	act_path = None
	try:
		with open(config_path, 'rt') as stream:
			act_path = Path(stream.readline().rstrip("\n")) or args.act
			while((path := stream.readline()) != ""):
				resource_dir_list.append(Path(path.rstrip("\n")))
	except(OSError):
		pass
	
	
	# TODO: Track which BWD2s have already been ported - don't port the same model multiple times!
	for i, filepath in enumerate(args.filepaths):
		dirpath = filepath.parent
		ext = filepath.suffix
		
		if(ext.lower() not in {".vdf", ".sdf", ".geo", ".map", ".odf"}):
			print(f"Invalid filepath #{i+1}: filepath must be a .vdf, .sdf, .geo, .map, or .odf file! Got \"{ext}\" from \"{filepath}\"")
			continue
		
		asset_resolver = AssetResolver(
			input_dirpath=dirpath,
			dest_dirpath=(args.dest or Path(os.getcwd())),
			resource_dir_list=resource_dir_list,
			act_path=act_path,
		)
		
		model_name = filepath.stem if args.name is None else args.name
		model_name += ".mesh"
		if(args.onlyonce and asset_resolver.get_output_mesh_path(model_name).exists()):
			print(f"Skipping {model_name}")
			continue
		
		settings = SettingsController(
			name=args.name,
			suffix=args.suffix,
			headlights=args.headlights,
			person=args.person,
			turret=args.turret,
			cockpit=args.cockpit,
			scope=ScopeSettings(
				scope=args.scope,
				type=args.scopetype,
				nation=args.scopenation,
				screen=None,
				gun_name=args.scopegun,
				transform=Transform(*args.scopetransform) if args.scopetransform is not None else None,
				texture=args.scopetexture,
			),
			no_pov_rots=args.nopovrots,
			flat_colors=args.flatcolors,
			boundingbox_scale_factors=BoundingBoxScaleFactors(*args.boundsmult) if args.boundsmult is not None else None,
			nowrite=args.nowrite,
			#verbose=args.verbose,
		)
		if(args.scopescreen is not None):
			settings.scope.screen = ScopeScreen(
				x=args.scopescreen[0],
				y=args.scopescreen[1],
				z=args.scopescreen[2],
				scale=args.scopescreen[3],
				behind_dist=args.scopescreen[4],
			)
		
		#asset_resolver.overwrite_textures = False
		#asset_resolver.overwrite_material = False
		#asset_resolver.overwrite_mesh = False
		#asset_resolver.overwrite_skeleton = False
		print("#==============================#")
		try:
			bwd2_path = None
			if(ext.lower() == ".odf"):
				# BWD2 PORT
				class_label, base_name, nation = portconfig_from_odf(filepath)
				print(f"classLabel: {class_label}, baseName: {base_name}, nation: {nation}")
				if(class_label == "person"):
					print("Class is person")
					if(settings.person is None):
						settings.person = True
					if(settings.turret is None):
						settings.turret = False;
				elif(class_label in {'turret', 'turrettank', 'howitzer'}):
					print("Class is turret/turrettank/howitzer")
					if(settings.person is None):
						settings.person = False
					if(settings.turret is None):
						settings.turret = True
				else:
					print("Class is not person nor turret/turrettank/howitzer")
					if(settings.person is None):
						settings.person = False
					if(settings.turret is None):
						settings.turret = False
				if(settings.scope.nation is None):
					settings.scope.nation = nation
				if(is_vehicle_type(class_label)):
					bwd2_path = asset_resolver.get_vdf_path(base_name)
					if(bwd2_path is None):
						raise Exception(f"VDF file not found: {base_name}")
				elif(is_building_type(class_label)):
					bwd2_path = asset_resolver.get_sdf_path(base_name)
					if(bwd2_path is None):
						raise Exception(f"SDF file not found: {base_name}")
				else:
					raise Exception(f"Bad GameObject; Unrecognized class label '{class_label}'")
					
				port_bwd2(bwd2_path, asset_resolver, settings)
				
			elif(ext.lower() in {".vdf", ".sdf"}):
				# BWD2 PORT
				port_bwd2(filepath, asset_resolver, settings)
				
			elif(ext.lower() == ".geo"):
				# GEO PORT
				port_geo(filepath, asset_resolver, settings)
				
			elif(ext.lower() == ".map"):
				# MAP PORT
				port_map(filepath, asset_resolver, settings)
			
		except Exception as e:
			print(f"!! Error handling file {i+1}: \"{filepath}\"")
			print(traceback.format_exc())
		print()
	

