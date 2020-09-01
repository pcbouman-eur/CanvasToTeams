from canvasapi import Canvas
import json
import os

# Do `pip install canvasapi` first before running this script!

DEFAULT_CANVAS_URL = 'https://eur.instructure.com'
DEFAULT_REMOVE_PATTERN = 'groep'
DEFAULT_ADD_PREFIX = 'Tutorial '
DEFAULT_IGNORE = 'Default section'

print('Please enter the Canvas base URL you want to use (default: '+DEFAULT_CANVAS_URL+')')
CANVAS_URL = input()
if len(CANVAS_URL.strip()) == 0:
    CANVAS_URL = DEFAULT_CANVAS_URL

print('Please enter your API token for Canvas')
print('You can create a Canvas acces token token for you account at '+CANVAS_URL+'/profile/settings')
API_KEY = input()

print('Please enter the Canvas course number. This is a number that appears in the URL when you go to your course')
COURSE_NUM = input()

canvas = Canvas(CANVAS_URL, API_KEY)
course = canvas.get_course(COURSE_NUM)
fname = 'course-'+str(course.id)+'-registrations.json'

print('Is there a text pattern you want to remove from the section information? (default: \''+DEFAULT_REMOVE_PATTERN+'\')')
REMOVE_PATTERN = input()
if len(REMOVE_PATTERN.strip()) == 0:
    REMOVE_PATTERN = DEFAULT_REMOVE_PATTERN

print('Is there a prefix you want to add to the section information? (default \''+DEFAULT_ADD_PREFIX+'\')')

ADD_PREFIX = input()
if len(ADD_PREFIX.strip()) == 0:
    ADD_PREFIX = DEFAULT_ADD_PREFIX

print('Are there channels that you do not want to map to channels? Separate them by commas (default: \''+DEFAULT_IGNORE+'\')')
SKIP_LIST = input()
if len(SKIP_LIST.strip()) == 0:
    SKIP_LIST = DEFAULT_IGNORE
SKIP_SET = {s.strip() for s in SKIP_LIST.split(',')}

print('Give a name for a channel to which all students should be added (leave empty to skip this step)')
CHANNEL_ALL = input()

data = {}
all_students = set()

print('Succesfully obtained the course. Please be patient while student enrollments are collected...')

for section in course.get_sections():
    enrollments = [enrollment for enrollment in section.get_enrollments()]
    secname = section.name.replace(REMOVE_PATTERN, '').strip()
    secname = ADD_PREFIX + secname
    students = list(sorted({e.sis_user_id for e in enrollments if e.role == 'StudentEnrollment' and not e.sis_user_id is None}))
    if not section.name in SKIP_SET:
        data[secname] = students
    all_students.update(students)
    none_students = [e for e in enrollments if e.sis_user_id is None]
    if len(none_students) > 0:
        print('The following students were not added to '+secname+' because the sis_user_id is missing')
        for ns in none_students:
            try:
                print(ns.user.name+' (id: '+ns.user.id+')')
            except:
                print(vars(ns))
    
if len(CHANNEL_ALL.strip()) != 0:
    data[CHANNEL_ALL] = list(sorted(all_students))

processed = False
if os.path.isfile(fname):
    # TODO: how to deal with multiple mutations??
    print('Old .json file found. Comparing the old file and the new data')
    with open(fname) as infile:
        old_data = json.load(infile)
    mutation = 1
    
    while True:
        mut_file = 'course-'+str(course.id)+'-mutation-'+str(mutation)+'.json'
        if not os.path.isfile(mut_file):
            break
        mutation += 1           
        with open(mut_file) as infile:
            mut_data = json.load(infile)
            for channel, std_list in mut_data.items():
                if not channel in old_data:
                    old_data[channel] = std_list
                else:
                    old_data[channel] = list({std for std in old_data[channel]}.union(set(std_list)))
    removed = 0
    for channel, std_list in old_data.items():
        if channel in data:
            for std in std_list:
                if std in data[channel]:
                    data[channel].remove(std)
                    removed += 1
    print('Removed '+str(removed)+' entries that were already added earlier')
    mutation = 1
    while True:
        fname = 'course-'+str(course.id)+'-mutation-'+str(mutation)+'.json'
        if os.path.isfile(fname):
            mutation += 1
        else:
            break       

count = sum([len(std_list) for std_list in data.values()])

if count > 0:
    with open(fname, 'w') as out:
        json.dump(data, out)
        print('Course registrations for '+str(count)+' students written to file: '+fname)
else:
    print('No new course registrations found. Not writing anything')
