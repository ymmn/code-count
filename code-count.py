import sys
import os
import re
import pdb

ONE_LINE_COMMENT_DELIMITER = {'py': '#',
                               'pde':'//',
                               'cpp':'//',
                               'c':'//',
                              'cu':'//'}

MULTI_LINE_COMMENT_DELIMITER = {'py': ('"""','"""'),
                                'pde':('/*','*/'),
                                'cpp':('/*','*/'),
                                'c':('/*','*/'),
                                'cu':('/*','*/') }

def get_extension(filename):
    ext = re.findall(r'\..+',filename)[0]
    return ext[1:]

def count_lines(extension,filepath):
    """
    Takes a source code file's extension and absolute file path,
    counts and return the number of lines that are:
    blank lines (only consists of whitespace)
    comment lines (only consists of comments/documentation)
    code lines (neither comment nor blank)
    """
    fil = open(filepath,'r')
    remaining_code = fil.readlines()
    blank_lines,remaining_code = count_blank_lines(remaining_code)
    commented_lines,remaining_code = count_commented_lines(remaining_code,extension)
    in_line_comments = count_inline_comments(remaining_code,extension)
    code_lines = len(remaining_code)
    return blank_lines, commented_lines, code_lines

def count_inline_comments(code,extension):
    """
    Takes code as an array of strings, extension as a string (e.g. 'py' for Python,
    'cpp' for C++), returns the count of in-line comments in code
    """
    comment_flag = ONE_LINE_COMMENT_DELIMITER[extension]
    count = 0
    for line in code:
        if comment_flag in line:
            count += 1
    return count

def count_commented_lines(code,extension):
    """
    Takes code as an array of strings, extension as a string (e.g. 'py' for Python,
    'cpp' for C++), counts the commented lines, removes them,
    and returns the number of commented lines and the code that remains
    """
    multi_line_flag = MULTI_LINE_COMMENT_DELIMITER[extension]
    single_line_flag = ONE_LINE_COMMENT_DELIMITER[extension]
    in_comment = False
    remaining_code = []
    num_lines = 0
    for line in code:
        stripped_line = line.lstrip()
        if stripped_line=="":
            continue
        is_single_comment = stripped_line[:len(single_line_flag)]==single_line_flag
        is_multi_comment = stripped_line[:len(multi_line_flag[0])]==multi_line_flag[0]
        if is_single_comment or is_multi_comment or in_comment: 
            num_lines += 1
        else:
            remaining_code.append(line)
        in_comment = detect_in_comment(stripped_line, multi_line_flag, in_comment)
    return num_lines,remaining_code

def count_blank_lines(code):
    """
    Takes code as an array of strings, counts the blank lines, removes them,
    and returns the number of blank lines and the code that remains
    """
    remaining_code = []
    blank_lines = 0
    for line in code:
        stripped_line = line.lstrip().rstrip()
        if stripped_line=='':
            blank_lines += 1
        else:
            remaining_code.append(stripped_line + "\n")
    return blank_lines,remaining_code

def detect_in_comment(line, mlc, comment_depth):
    """
    Given a line, the multi-comment delimiters for this code, and whether or not we're
    already in a comment, returns true if the line counts as a comment or not.
    """
    comment_depth += line.count(mlc[0]) # python will treat True as 1, and False as 0
    comment_depth -= line.count(mlc[1])
    return comment_depth > 0

def get_short_filename(filename):
    """
    get relative filename out of absolute filename (i.e. take out the path to
    current directory)
    """
    return filename[len(os.getcwd())+1:]

def get_max_filename_length():
    """
    Get the length of the largest filename to determine how wide the "name" 
    column needs to be in the output
    """
    return reduce( max,  # feeling fancy
                   map( lambda x: len(get_short_filename(x)),
                        source_files),
                   len('Total'))

def format_output(name,loc,blank,comment):
    """
    Prints out the output in neat table format. 
    """
    x = get_max_filename_length()
    print ("%"+str(x)+"s %10s %10s %10s") %(name,loc,blank,comment)


source_files = []
for arg in sys.argv[1:]:
    if arg[0]=='.': # get full file path names
        source_files.append(os.getcwd() + arg[1:])

tot_code, tot_white, tot_comment = 0,0,0
format_output("Name","LOC","Blank","Comments")
for src_file in source_files:
    white_lines,comment_lines,code_lines = count_lines(get_extension(src_file),src_file)
    format_output(get_short_filename(src_file), code_lines, white_lines, comment_lines)
    tot_code += code_lines
    tot_white += white_lines
    tot_comment += comment_lines
format_output('Total', tot_code, tot_white, tot_comment)

