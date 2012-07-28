'''
Created on 25.07.2012

@author: breno
'''

import os.path
import sys
import string
import random
import glob
from werkzeug.utils import secure_filename


class FileSystem(object):
    '''
    Wrapper to read and write operations on a file system sandbox
    '''
    
    def __init__(self, sandbox):
        '''
        Constructor
        '''
        self.sandbox = os.path.normpath(sandbox)
        assert(os.path.exists(self.sandbox))
        
    
    def __safe_path(self, path):
        # avoid someone getting out of the sandbox by adding '..' to the path:
        directory = os.path.normpath(os.path.join(self.sandbox, path))
        assert(os.path.commonprefix([directory, self.sandbox]) == self.sandbox)
        return directory
    
    def split(self, path):
        directory = self.__safe_path(path)
        return os.path.split(directory)
    
    def touch(self, filename, path):
        directory = self.__safe_path(path)
        # TODO check if file exists
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except OSError:
                print "permission denied"
                sys.stdout.flush()
        f = open(os.path.join(directory, filename), 'w')
        f.write("")
        f.close()
        
    def is_dir(self, path):
        directory = self.__safe_path(path)
        return os.path.isdir(directory)
    
    def ls(self, path):
        directory = self.__safe_path(path)
        # assert the path is a dir or a wildcard expansion
        assert(os.path.isdir(directory) or '*' in directory)
        if ('*' in directory):
            listdir = [self.split(x)[1] for x in glob.glob(directory)]
            directory = self.split(directory)[0]
        else:
            listdir = os.listdir(directory)
        return [{'name':a, 
                   'file':os.path.isfile(os.path.join(directory, a)), 
                   'size':os.path.getsize(os.path.join(directory, a)),
                   'lastmodified':os.path.getmtime(os.path.join(directory, a))} for a in listdir]
        
    def mkdir(self, path, name):
        directory = self.__safe_path(path)
        # assert the path is a dir
        assert(os.path.isdir(directory))
        os.mkdir(os.path.join(directory, name))
        
    def save(self, path, fil, force):
        directory = self.__safe_path(path)
        filename = secure_filename(fil.filename)
        if os.path.exists(os.path.join(directory, filename)) and not force:
            filename_split = filename.split('.')
            extension = ""
            if len(filename_split) > 1:
                extension = filename_split[-1]
            filename = ''.join(filename_split[:-1]) + ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(3)) + '.' + extension
        fil.save(os.path.join(directory, filename))
        
    def delete(self, path):
        fil = self.__safe_path(path)
        if (os.path.isfile(fil)):
            os.remove(fil)
        else:
            os.removedirs(fil)
