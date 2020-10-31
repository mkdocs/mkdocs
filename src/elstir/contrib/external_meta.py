# --------------------------------------------
# Main part of the plugin
#
# JL Diaz (c) 2019
# MIT License
# --------------------------------------------
from collections  import defaultdict
from pathlib import Path
import os
import yaml
import jinja2
from elstir.structure.files import File
from elstir.structure.nav import Section
from elstir.plugins import BasePlugin
from elstir.config.config_options import Type


class ExternalMetaPlugin(BasePlugin):

    # config_scheme = (
    #     ('tags_filename', Type(str, default='tags.md')),
    #     ('tags_folder', Type(str, default='aux')),
    #     ('tags_template', Type(str)),
    # )

    def __init__(self):
        self.metadata = []
        self.tags_filename = "tags.md"
        self.tags_folder = "aux"
        self.tags_template = None

    def on_nav(self, nav, config, files):
        # nav.items.insert(1, nav.items.pop(-1))
        pass

    # def on_config(self, config):
    #     # Re assign the options
    #     self.tags_filename = Path(self.config.get("tags_filename") or self.tags_filename)
    #     self.tags_folder = Path(self.config.get("tags_folder") or self.tags_folder)
    #     # Make sure that the tags folder is absolute, and exists
    #     if not self.tags_folder.is_absolute():
    #         self.tags_folder = Path(config["docs_dir"]) / ".." / self.tags_folder
    #     if not self.tags_folder.exists():
    #         self.tags_folder.mkdir(parents=True)

    #     if self.config.get("tags_template"):
    #         self.tags_template = Path(self.config.get("tags_template"))

    def on_files(self, files, config):
        # Scan the list of files to extract tags from meta
        print(f"inside external_meta: {config}")
        # for f in files:
        #     if not f.src_path.endswith(".md"):
        #         continue
        #     self.metadata.append(get_metadata(f.src_path, config["docs_dir"]))

        # # Create new file with tags
        # self.generate_tags_file()

        # # New file to add to the build
        # newfile = File(
        #     path=str(self.tags_filename),
        #     src_dir=str(self.tags_folder),
        #     dest_dir=config["site_dir"],
        #     use_directory_urls=False
        # )
        # files.append(newfile)

    # def generate_tags_file(self):
    #     sorted_meta = sorted(self.metadata, key=lambda e: e.get("year", 5000) if e else 0)
    #     tag_dict = defaultdict(list)
    #     for e in sorted_meta:
    #         if not e:
    #             continue
    #         if "title" not in e:
    #             e["title"] = "Untitled"
    #         tags = e.get("tags", [])
    #         if tags is not None:
    #             for tag in tags:
    #                 tag_dict[tag].append(e)

    #     t = self.generate_tags_page(tag_dict)

    #     with open(str(self.tags_folder / self.tags_filename), "w") as f:
    #         f.write(t)

# Helper functions

def get_metadata(name, path):
    # Extract metadata from the yaml at the beginning of the file
    def extract_yaml(f):
        result = []
        c = 0
        for line in f:
            if line.strip() == "---":
                c +=1
                continue
            if c==2:
                break
            if c==1:
                result.append(line)
        return "".join(result)

    filename = Path(path) / Path(name)
    with filename.open() as f:
        metadata = extract_yaml(f)
        if metadata:
            meta = yaml.load(metadata, Loader=yaml.FullLoader)
            meta.update(filename=name)
            return meta
