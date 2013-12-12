import re
import subprocess
import os

from base_linter import BaseLinter

CONFIG = {
    'language': 'HTML (Twig)',
}

CURRENT_PATH = os.path.dirname(__file__.encode('utf-8'))
LIB_PATH = os.path.abspath(os.path.join(CURRENT_PATH, u'libs'))
TEMPFILES_PATH = os.path.abspath(os.path.join(CURRENT_PATH, u'..', u'.tempfiles'))
if not os.path.exists(TEMPFILES_PATH):
    os.mkdir(TEMPFILES_PATH)

class Linter(BaseLinter):
    phpcode = 'try { \
        include(\''+LIB_PATH+'/Twig/Autoloader.php\'); \
        \
        Twig_Autoloader::register(); \
        $loader = new Twig_Loader_String(); \
        $twig = new Twig_Environment($loader); \
        $twig->registerUndefinedFunctionCallback(function($funcname) { \
            return new Twig_Function_Function(\'printf\', array(\'is_safe\' => array(\'all\'))); \
        }); \
        $twig->parse($twig->tokenize(file_get_contents(\'#filepath#\'))); \
    } \
    catch (Twig_Error_Syntax $exception) { \
        printf(\'%d %s\', $exception->getTemplateLine(), $exception->getRawMessage());\
    }'
    
    def built_in_check(self, view, code, filename):
        executable = self.get_mapped_executable(view, "php")

        tempfilename = u'view{0}'.format(view.id())
        tempfilepath = os.path.join(TEMPFILES_PATH, tempfilename)
        with open(tempfilepath, 'w') as f:
            f.write(code)
        
        phpcode = self.phpcode.replace("#filepath#", tempfilepath);
        args = executable + (' -r "%s"' % phpcode)
        
        try:
            process = subprocess.Popen(args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                startupinfo=self.get_startupinfo())
            result = process.communicate()[0]
        finally:
            os.remove(tempfilepath)

        return result.strip()
  
    def parse_errors(self, view, errors, lines, errorUnderlines, violationUnderlines, warningUnderlines, errorMessages, violationMessages, warningMessages):
        match = re.match(r'^(\d+) (.+)$', errors)
        
        if match:
            line, error = match.group(1), match.group(2)
            self.add_message(int(line), lines, error, errorMessages)
