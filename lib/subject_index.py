import re
from slugify import slugify
from .general_utility import read_in_file, safe_open_w, get_link_from_file_path, build_links_for_all_headers

# https://stackoverflow.com/questions/14692690/access-nested-dictionary-items-via-a-list-of-keys
def store_subject_link(subject_map, keys_in_order_of_access, link_title, link_value):
  # We create dictionaries as many levels deep as we need to.
  # This loop sets the subject_map variable to another nested
  # dictionary each iteration, leaving us ended with the variable
  # referencing the dictionary we want to be assigning the new link in
  for key in keys_in_order_of_access:
    subject_map = subject_map.setdefault(key, {})
  subject_map[link_title] = link_value




def build_single_subject_link(match_obj, page_path, study_title, page_title, header_title, subject_map):
  
  subject = match_obj.group(1)

  slugified_section_header = slugify(header_title)
  slugified_subject = slugify(subject)
  nested_subject_topics = subject.split(' > ')

  # Escape quotes, so that when this is injected in a Hugo shortcode, quoted headers are supported
  study_title = study_title.replace('"', '\\"')
  page_title = page_title.replace('"', '\\"')
  header_title = header_title.replace('"', '\\"')
  
  subject_index_link_title = f'{study_title} | {page_title} | {header_title}'

  # Only add header id to link path when appropriate
  subject_index_link_value = f'{get_link_from_file_path(page_path)}/'
  if slugified_section_header != "":
    subject_index_link_value = subject_index_link_value + f'#{slugified_section_header}'

  subject_map = store_subject_link(subject_map, nested_subject_topics, subject_index_link_title, subject_index_link_value)
  
  return f'<a href="/subject-index/#{slugified_subject}">{subject}</a>'



'''
The subjects section is ignored in three cases:

{{< subjects >}}

{{< /subjects >}}

{{< subjects >}}
{{< /subjects >}}

{{< subjects >}}{{< /subjects >}}

These cases correspond to .Inner lengths of 4, 2, and 0, respectively.
So we only render the shortcode if .Inner's length is not 4, 2, or 0.

See the subjects.html shortcode
'''
subject_re_pattern = re.compile(r'(?:<a .+?>)?([^<\n]+)(?:<\/a>)?', re.MULTILINE)
def build_single_subjects_section(match_obj, page_path, study_title, page_title, subject_map):

  header_and_opening_tag = match_obj.group(1)
  header_title = match_obj.group(2)
  subjects_section = match_obj.group(3)
  closing_tag = match_obj.group(4)

  # If the header title came in as None, it means we matched a subjects section without an associated header
  # Subject links to a page as a whole will not have any header defined
  # This uses an empty string to signify there is no header, rather than None
  if header_title == None:
    header_title = ""

  new_subjects_section = subject_re_pattern.sub(lambda match: build_single_subject_link(match, page_path, study_title, page_title, header_title, subject_map), subjects_section)

  return (header_and_opening_tag + new_subjects_section + closing_tag)

header_and_subjects_section_re_pattern = re.compile(r'^((?:#+ (.+) \{\#.+\}\n\n)?{{< subjects >}})((?:.|\n)+?)({{< \/subjects >}})', re.MULTILINE)
def build_subjects_sections_on_page(file_path, file_as_string, study_title, page_title, subject_map):
  new_file_content = build_links_for_all_headers(file_as_string)
  new_file_content = header_and_subjects_section_re_pattern.sub(lambda match: build_single_subjects_section(match, file_path, study_title, page_title, subject_map), new_file_content)
  return new_file_content




subjects_section_re_pattern = re.compile(r'^{{< subjects >}}(?:.|\n)+?{{< \/subjects >}}', re.MULTILINE)
def strip_subjects_sections(content_section):
  content_section_without_subjects_sections = subjects_section_re_pattern.sub('', content_section)
  return content_section_without_subjects_sections






def get_content_type_name(link, content_types):
  for path, name in content_types.items():
    if(path in link):
      return name

def get_content_type_slugified(link, content_types):
  for path, name in content_types.items():
    if(path in link):
      if('/' in path):
        return path.split('/')[0]
      else:
        return path

def build_header_on_subject_index_page(topic):
  markdown_header_prefix = '##'
  levels_nested = topic.count('>')
  for i in range(levels_nested):
    markdown_header_prefix = markdown_header_prefix + '#'
  return markdown_header_prefix + ' ' + topic



def add_links_for_topic(output, topic, topic_dict, content_types):
  
  leaf_titles = []
  child_topic_keys = []
  
  for key, value in topic_dict.items():
    if(type(value) is str):
      leaf_titles.append(key)
    else: # type(value) is dict
      child_topic_keys.append(key)
  
  output = output + build_header_on_subject_index_page(topic) + '\n\n'
  
  leaf_titles = sorted(leaf_titles)
  for title in leaf_titles:

    split_title = title.split(" | ")
    study_title = split_title[0]
    page_title = split_title[1]
    header_title = split_title[2]

    link = topic_dict[title]
    content_type_name = get_content_type_name(link, content_types)
    content_type_slugified = get_content_type_slugified(link, content_types)

    # Only add header to subject index link if it is defined
    # Subject links to a page as a whole will not have any header defined
    header_parameter = ""
    if(header_title != ""):
      header_parameter = f'header-title="{header_title}"'

    output = output + f'''{{{{% subject-index-link
content-type="{content_type_name}"
content-type-slugified="{content_type_slugified}"
link="{link}"
study-title="{study_title}"
page-title="{page_title}"
{header_parameter}
%}}}}
\n'''
    
  child_topic_keys = sorted(child_topic_keys)
  for child_topic in child_topic_keys:
    output = output + add_links_for_topic('', topic + ' > ' + child_topic, topic_dict[child_topic], content_types)

  return output




subject_index_replacement_re_pattern = re.compile(r'^<!-- subject-index -->(?:.|\n)+<!-- subject-index -->', re.MULTILINE)
def build_subject_index(subject_map, content_directory, content_types):
  
  output = ''
  topics = sorted(subject_map.keys())
  for topic in topics:
    output = add_links_for_topic(output, topic, subject_map[topic], content_types)

  output = build_links_for_all_headers(output)

  subject_index_path = content_directory + 'subject-index.md'

  file_content = read_in_file(subject_index_path)
  with safe_open_w(subject_index_path) as f:
    new_file_content = subject_index_replacement_re_pattern.sub(
      f'<!-- subject-index -->\n\n{output}\n\n<!-- subject-index -->',
      file_content
    )
    f.writelines(new_file_content)













example_subjects_section = '''Jesus Christ > Divinity
God > Omniscience > Foreknowledge
God > Character of
'''

example_subjects_section_a_tags = '''<a href="/subject-index/#subject-1">God > Character of</a>
<a href="/subject-index/#subject-2">God > Omniscience > Foreknowledge</a>
<a href="/subject-index/#subject-3">Jesus Christ > Divinity</a>
'''

'''
Scratch


subject_map = {}
store_subject_link(subject_map, ["God"], 'Theology, §<em>Section 1</em>', "/shorter-topical-studies/theology/#section1")
store_subject_link(subject_map, ["God"], 'Theology, §<em>Section 2</em>', "/longer-topical-studies/theology/#section2")
store_subject_link(subject_map, ["God", "Omniscience"], 'Theology, §<em>Omniscience</em>', "/questions-and-answers/self-generated/theology/#omniscience")
store_subject_link(subject_map, ["God", "Omnipotence"], 'Theology, §<em>Omnipotence</em>', "/questions-and-answers/reader-correspondence/theology/#omnipotence")
store_subject_link(subject_map, ["God", "Omniscience", "Foreknowledge"], 'Theology, §<em>Foreknowledge</em>', "/verse-by-verse-studies/theology/#omniscience")

build_subject_index(subject_map)




build_subjects_section(example_subjects_section, '/shorter-topical-studies/study-1', 'Study 1', 'This is a header', subject_map)
build_subjects_section(example_subjects_section_a_tags, '/longer-topical-studies/study-2', 'Study 2', 'A fantastic section', subject_map)

print(subject_map)




'''