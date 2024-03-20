import re

markdown_header_re_pattern = re.compile('([#]+ .*)')
title_slide_break_re_pattern = re.compile('---\n')

def remove_duplicates_from_list_while_preserving_order(input_list):
  seen = set()
  seen_add = seen.add
  return [x for x in input_list if not (x in seen or seen_add(x))]

def add_appropriate_things_to_beginning_and_end_of_slides(content_section, summary):
  
  headers = markdown_header_re_pattern.findall(content_section)

  # Remove duplicates = repeated slide headers
  headers = remove_duplicates_from_list_while_preserving_order(headers)

  outline_as_string = ''
  # Slide links start at 4, since we will not link to the title slide, the summary slide,
  # nor the outline itself
  slide_number = 4

  # The first header is the title slide, so we skip it
  for header in headers[1:]:
    
    # Get rid of number signs that indicate headers in Markdown
    header_without_number_signs = header.replace('#', '').strip()

    outline_item = '- [' + header_without_number_signs + '](#' + str(slide_number) + ')\n'

    # Add indentation if the header is h4 or h5.
    # Four spaces for h5
    if('#####' in header):
      outline_item = '     ' + outline_item
    # And two spaces for h4
    elif('####' in header):
      outline_item = '  ' + outline_item

    outline_as_string += outline_item
    slide_number += 1
  
  # Define content for summary slide
  summary_slide = '### Summary\n\n' + summary + '---\n\n'
  
  # Add a header to outline, and also a trailing new line
  outline_slide = '#### Outline\n\n' + outline_as_string + '\n'

  #settings_slide = '---\nReftagger control panel\n\n'

  # Actually add the newly-constructed outline to the markdown. Add it right after the title slide, and at the very end of the presentation
  # lines = title_slide_break_re_pattern.sub(settings_slide + outline_as_string + '---\n', lines, 1)
  
  # Add summary and outline to beginning
  content_section = title_slide_break_re_pattern.sub('---\n\n' + summary_slide + outline_slide + '---\n', content_section, 1)
  
  # Add outline to end
  content_section += "\n\n---\n\n" + outline_slide

  return content_section