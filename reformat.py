import glob
from bs4 import BeautifulSoup
import codecs
import os
from datetime import datetime
import hashlib
import copy

def read(blob):
    soup = BeautifulSoup(blob, "html5lib")
    return soup



# input  (from wget)
#       /scratch/wiki.tudelft.nl/.../

web_start_dir = "/scratch/wiki.tudelft.nl/bin/view/Research/ISO19152/"
web = "ISO19152"

# web_start_dir = "/scratch/wiki.tudelft.nl/bin/view/Organisation/OTB/GISt/"
# web = "GISt"

filenames = [
    filename
    for filename in sorted(glob.glob(web_start_dir + "*"))
    if not filename.endswith(".orig")
]

# output:
#       /scratch/WikiWebs/<web>/<assets>

work_dir = "/scratch"
output_dir = os.path.join(work_dir, "WikiWebs", web)

os.makedirs(output_dir, exist_ok=True)
os.makedirs(os.path.join(output_dir, "assets"), exist_ok=True)

stems = [filename.replace(web_start_dir, "") for filename in filenames]

## go over all files and make a toc (not used)
# list_items = "\n".join(
#     [f'<li><a href="{filename}">{filename}</a></li>' for filename in stems]
# )
# toc = f"""
# <ul class="w3-ul w3-tiny">
#   {list_items}
# </ul>
# """



header_tpl = """<!DOCTYPE html>
<html lang="en">
<head>
<title>{title}</title>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="">

<link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">

<style>
.content {{
  max-width: 80em;
  margin-top: 1em;
  margin-bottom: 1em;
  margin-left: 1em;
  margin-right: auto;
  padding: 0.25em;
}}

.foswikiToc 
{{
  background-color: #eee;
  padding: 0.5em;
  font-size: small;
}}

.mm-menu ul {{
    list-style-type: none;
    list-style: none;
    margin: 0 0 0 0.75em;
    padding: 0em;
}}
/*
.mm-menu ul > li > ul {{
    list-style-type: none;
    margin: 0;
    padding: 0;
}}
.mm-menu ul > li > ul > li > ul {{
    list-style-type: none;
    margin: 0;
    padding: 0;
}}
*/
</style>

</head>
<body>
<div class="content w3-row">
  <div class="w3-container w3-threequarter">
"""



### traverse bread crumbs to create hieararchical menu
page_paths = []
for filename, stem in zip(filenames, stems):

    with codecs.open(filename, encoding="iso-8859-1") as fh:
        content = fh.read()
    soup = read(content)
    place_in_tree_structure = copy.copy(soup.find("div", {'class': 'tudelftTop'}))
    if place_in_tree_structure:
        separators = place_in_tree_structure.find_all('span', {"class": "foswikiSeparator"})
        links = place_in_tree_structure.find_all('a')
        if links:
            page_path = [(link.get('href'), link.string) for link in links[:len(separators)+1]]
            page_paths.append(page_path)

tree = {}
root = None
for page_path in sorted(page_paths):
    root = page_path[0]
    for parent, child in zip(page_path, page_path[1:]):
        if parent not in tree:
            tree[parent] = {'childs': set([])}
        tree[parent]['childs'].add(child)
    
def traverse(node, depth, buf):
    if node[1].lower().startswith("web"):
        return
    print(" "*depth, "<ul>", file=buf)
    if node[0].startswith('https'):
        print(" "*depth, "<li>WikiWeb", file=buf)
    else:
        print(" "*(depth+1), f"<li><a href='{node[0]}'>", node[1], "</a>", file=buf)
    if node in tree:
        for kid in sorted(tree[node]['childs']):
            traverse(kid, depth + 1, buf)
    print(" "*(depth+1), "</li>", file=buf)
    print(" "*depth, "</ul>", file=buf)
from io import StringIO
buf = StringIO()
traverse(root, 0, buf)
menu_hierarchy = buf.getvalue()

# duplicate list (but with all pages)
# not used
menu_list = "<ul>"
for filename, stem in zip(filenames, stems):
    menu_list += f"<li><a href='{stem}'>{stem}</a></li>"
menu_list += "</ul>"

toc = f"""
<div class="mm-menu w3-small">
<h4>WikiWeb &middot; Hierarchy</h4>
  {menu_hierarchy}
</div>
<div class="mm-menu w3-small">
<h4>WikiWeb &middot; Lists</h4>
  <ul>
    <li><a href="WebHome">WebHome</a></li>
    <li><a href="WebTopicList">WebTopicList</a></li>
    <li><a href="WebIndex">WebIndex</a></li>
  </ul>
  <!--
  {menu_list}
  -->
</div>
"""

now = datetime.now()
dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
footer = f"""</div>
  <div class="w3-container w3-quarter">
  

    {toc}
    <span class="w3-tiny">Reformatted page at: {dt_string}</span>
  </div>
</div>
</div></body></html>"""

for filename, stem in zip(filenames, stems):

    with codecs.open(filename, 
    encoding="iso-8859-15"
    # encoding="windows-1252"
    ) as fh:
        content = fh.read()
        content = content.replace("<p></p>", "</p><p>")
        soup = read(content)

        for x in soup.find_all():
            # fetching text from p tag and remove whitespaces
            if x.name == "p" and len(x.get_text(strip=True)) == 0:
                # Remove empty p tags from the dom
                x.extract()


        # will be placed inside html title, by header template
        title = container = soup.find("title")
        print()
        print(filename)
        print(title.text)
        print("-" * 80)

        header = header_tpl.format(title=title.text)
        container = soup.find("div", {"id": "tudelftMainContents"})

        # print(container)
        if container:
            # remove broadcast message div
            broadcasts = container.find_all("div", {"class": "foswikiBroadcastMessage"})
            for tag in broadcasts:
                # tag["class"] = tag.get("class", []) + ["w3-tiny"]
                tag.extract()


            to_remove = container.find_all("div", {"class": "tudelftTopicAction"})
            for tag in to_remove:
                tag.extract()
                
            to_remove = container.find_all("span", {"class": "tudelftToolBar"})
            for tag in to_remove:
                tag.extract()
                

            # add w3-small class to specific div's (so that their font beccomes smaller)
            for relevant in [
                "tudelftTop",
                "tudelftInfo",
                "tudelftBorder",
                "foswikiContentFooter",
            ]:
                tags = container.find_all("div", {"class": relevant})
                for tag in tags:
                    tag["class"] = tag.get("class", []) + [
                        "w3-small w3-container w3-light-grey"
                    ]

            for relevant in ["tudelftContent"]:
                tags = container.find_all("div", {"class": relevant})
                for tag in tags:
                    tag["class"] = tag.get("class", []) + ["w3-margin w3-padding-16"]

            # local links that we preserve
            tags = container.find_all("img")
            for tag in tags:
                print("🖼️", tag.get("src"))
                href = tag.get("src")
                if href and href.startswith("../"):
                    intersperse = "⚙️" + web_start_dir + href
                    with open(web_start_dir + href, "rb") as fh:
                        print(fh.name)
                        old_path = fh.name
                        old_path_list = old_path.split("/")
                        old_basename = old_path_list[-1]
                        new_name = hashlib.md5(
                            "".join(old_path_list[:-1]).encode("utf-8")
                        ).hexdigest()[:6]
                        contents = fh.read()

                    out_filename_web = os.path.join(
                        "assets", new_name + "__" + old_basename
                    )
                    with open(os.path.join(output_dir, out_filename_web), "wb") as fh:
                        fh.write(contents)
                    tag["src"] = out_filename_web
            #
            tags = container.find_all("a")
            for tag in tags:
                intersperse = ""
                href = tag.get("href")
                if href and href.startswith("../"):

                    intersperse = "⚙️" + web_start_dir + href
                    with open(web_start_dir + href, "rb") as fh:
                        print(fh.name)
                        old_path = fh.name
                        old_path_list = old_path.split("/")
                        old_basename = old_path_list[-1]
                        new_name = hashlib.md5(
                            "".join(old_path_list[:-1]).encode("utf-8")
                        ).hexdigest()[:6]
                        contents = fh.read()

                    out_filename_web = os.path.join(
                        "assets", new_name + "__" + old_basename
                    )
                    with open(os.path.join(output_dir, out_filename_web), "wb") as fh:
                        fh.write(contents)
                    tag["href"] = out_filename_web
                print(
                    "🔗",
                    intersperse,
                    tag.get("href"),
                    tag.text,
                    "|",
                    tag.string,
                    "|",
                    tag.get("id"),
                    tag.get("name"),
                )

            links = container.find_all("a")
            for tag in links:
                href = tag.get("href")
                if href is not None and (
                    href.startswith("https://wiki.tudelft.nl")
                    or href.startswith("http://wiki.tudelft.nl")
                ):
                    tag.unwrap()
                    # print("removing internal link", href)

            # remove font tags, putting content into their parent tags
            font_tags = container.find_all("font")
            for tag in font_tags:
                tag.unwrap()

            font_tags = container.find_all("span")
            for tag in font_tags:
                tag.unwrap()

            # font_tags = container.find_all('strong')
            # for tag in font_tags:
            #     tag.unwrap()

            out_filename = os.path.join(output_dir, stem)
            print(out_filename)
            with codecs.open(out_filename, "w", "utf-8") as fh:
                # with open(out_filename, "w") as fh:
                val = container.prettify(formatter="html")
                fh.write(header)
                fh.write(val)
                fh.write(footer)
