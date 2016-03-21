#!/usr/bin/env python
# -*- coding: utf-8 -*-

# --------------------------------
# Author: shenjh@snail.com
# Date: 2015/7/29
# Usage:
# --------------------------------

import BaseHTTPServer, cgi, SocketServer, datetime, json, traceback, hashlib, logging, MySQLdb, MySQLdb.cursors
from os import path, makedirs
from urlparse import urlparse, parse_qs

MYSQL_HOST = "192.168.19.140"
MYSQL_USER = "shenjh"
MYSQL_PASSWD = "shenjh"
MYSQL_DB = "ujobs"
UPLOAD_DIR = "E:/opt/uploads/"
SERVER_BIND_IP = '0.0.0.0'
SERVER_BIND_PORT = 8083
MAX_UPLOAD_SIZE = 100

logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s][%(filename)s][line:%(lineno)d][%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='fileserver.log',
                    filemode='w')

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s][%(filename)s][line:%(lineno)d][%(levelname)s] %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


class MysqlHandler(object):
    db = None
    cursor = None

    def __init__(self):
        if not self.cursor:
            self.cursor = self.get_connection().cursor()

    def get_connection(self):
        if not self.db:
            self.db = MySQLdb.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWD, MYSQL_DB, charset='utf8',
                                      cursorclass=MySQLdb.cursors.DictCursor)
        return self.db

    def close_connection(self):
        if not self.db:
            self.db.close()

    def get_file_info(self, md5sum):
        cursor = self.cursor
        sql = "SELECT * FROM files_fileinfo WHERE `md5sum`='%s' ORDER BY `id` DESC" % (md5sum)
        cursor.execute(sql)
        data = cursor.fetchall()
        # print "file_info:", data
        if data:
            return data[0]
        return None

    def insert_file_info(self, file_name, size, md5sum, path, upload_time):
        cursor = self.cursor
        sql = "INSERT INTO `files_fileinfo` (`file_name`, `size`, `md5sum`, `path`, `upload_time`)  " \
              "VALUES ('%s',%s,'%s','%s','%s');" % (file_name, size, md5sum, path, upload_time)
        logging.debug("insert_file_info sql:%s" % sql)
        try:
            data = cursor.execute(sql)
            self.db.commit()
            if data == 1:
                sql = "SELECT id from `files_fileinfo` where `md5sum`='%s' ORDER BY `id` DESC ;" % (md5sum)
                cursor.execute(sql)
                info = cursor.fetchone()
                logging.debug("file_info:%s" % info)
                return info
        except:
            error = traceback.format_exc()
            logging.error(error)
            self.db.rollback()
        return None

    def insert_upload_record(self, info_id, file_name, username="", src_ip="", remote_path="", remote_account=None,
                             location_type=1):
        if not remote_path:
            remote_path = file_name
        cursor = self.cursor
        upload_time = datetime.datetime.now()
        sql = "INSERT INTO `files_uploadrecord` (`user_name`, `fileinfo_id`, `file_name`, `upload_time`, `src_ip`, `location_type`, `remote_path`) " \
              "VALUES ('%s', %s, '%s', '%s', '%s', %s, '%s');" % (
                  username, info_id, file_name, upload_time, src_ip, location_type, remote_path)
        try:
            logging.debug("upload_record sql:%s" % sql)
            data = cursor.execute(sql)
            self.db.commit()
            if data == 1:
                sql = "SELECT * from `files_uploadrecord` where `user_name`='%s' and `fileinfo_id`=%s and `upload_time`='%s';" % (
                    username, info_id, upload_time)
                cursor.execute(sql)
                record = cursor.fetchone()
                logging.debug("upload record:%s" % record)
                return record
        except:
            error = traceback.format_exc()
            logging.error(error)
            self.db.rollback()
        return None


class WebHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        handler = None
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.send_error(404, 'Please input file md5, URI: /?md5=xxxx')
            return
        try:
            src_ip = self.client_address[0]
            logging.info("Receive file pull request, src_ip:{0}, path:{1}".format(src_ip, self.path))
            query_components = parse_qs(urlparse(self.path).query)
            logging.debug("query params:%s" % query_components)
            md5 = query_components.get("md5", [])
            if not md5 or not isinstance(md5,list) or not md5[0]:
                self.send_error(400, 'Bad request: %s' % self.path)
                return
            handler = MysqlHandler()
            info = handler.get_file_info(md5[0])
            if not info:
                raise IOError
            logging.debug("file full path: %s" % (UPLOAD_DIR + "/" + info['path']))
            f = open(UPLOAD_DIR + info['path'], 'rb')
            self.send_response(200)
            self.send_header('Content-Type', 'application/octet-stream')
            self.send_header('Content-Disposition', 'attachment;filename="%s"'%(info['file_name'].encode('gb2312')))
            self.end_headers()
            self.wfile.write(f.read())
            f.close()
        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)
        except Exception:
            logging.error(traceback.format_exc())
            self.send_error(500, 'Some Error occurred')
        finally:
            if handler:
                handler.close_connection()

    def do_POST(self):
        """
            params: send_file_username, send_file_hash, upField.
        """
        status = 500
        data = {}
        mysql_handler = None
        try:
            form = cgi.FieldStorage(fp=self.rfile, headers=self.headers,
                                    environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': self.headers['Content-Type'], })
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            src_ip = self.client_address[0]
            username = form['send_file_username'].value
            record = {}
            file_hash = form["send_file_hash"].value
            file_field = form["upField"]
            logging.info(
                "Start file post request, username:{0},file_hash:{1}, src_ip:{2}".format(username, file_hash, src_ip))
            # logging.debug("headers: %s" % (self.headers))
            if file_field.filename:
                filename = file_field.filename
                mysql_handler = MysqlHandler()
                info = mysql_handler.get_file_info(file_hash)
                if info and path.exists(UPLOAD_DIR + info['path']):
                    logging.info("file already existed in file server.")
                    data.update({'msg': 'file exist,ignore save.'})
                else:
                    store_file_name = 'file_' + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                    folder = self.get_sub_dir_name()
                    s_path = folder + store_file_name
                    s_path = s_path if not info else info['path']
                    full_path = UPLOAD_DIR + s_path
                    if not path.isdir(path.dirname(full_path)):
                        makedirs(path.dirname(full_path))
                    i = 0
                    s_hash = ""
                    file_len = 0
                    while i < 3 and s_hash != file_hash:
                        logging.debug("write path: {0}".format(full_path))
                        upfile = open(full_path, 'wb+')
                        file_data = file_field.file.read()
                        upfile.write(file_data)
                        md5obj = hashlib.md5()
                        md5obj.update(file_data)
                        s_hash = md5obj.hexdigest()
                        upfile.close()
                        i += 1
                        file_len = len(file_data)
                        del file_data
                        if file_len > MAX_UPLOAD_SIZE * 1024 * 1024:
                            raise RuntimeError("file size too big, max: {0}MB, current: {1}".format(MAX_UPLOAD_SIZE,self.format_bytes(file_len)))

                    logging.debug("save path:{0}, check_hash:{1}".format(s_path, s_hash))
                    if s_hash != file_hash:
                        data.update({'msg': "md5 not match, new file save fail"})
                        logging.error(
                            "New file save fail, hash not match, given:{0},actually:{1}".format(file_hash, s_hash))
                        raise RuntimeError("md5 not match, new file save fail")
                    else:
                        if not info:
                            info = mysql_handler.insert_file_info(filename, file_len, file_hash, s_path,
                                                              datetime.datetime.now())
                            logging.debug("new fileinfo created, new_id:%s"%(info['id']))
                            data.update({'msg': 'file info created'})
                        else:
                            logging.debug("file missing, using old fileinfo, old_id:%s"%(info['id']))
                            data.update({'msg': 'file info updated'})
                        logging.debug(
                            "New file save ok, src_ip:{4},file_hash:{0}, length:{1}, file_name:{2}, username:{3}".format(
                                file_hash, file_len, filename, username, src_ip))

                if info:
                    record = mysql_handler.insert_upload_record(info['id'], filename, username=username, src_ip=src_ip)
                if record:
                    status = 200
                    data.update({
                        'record_id': record.get("id"),
                        'file_id': info['id']
                    })
                else:
                    logging.warning("Record create fail")
                    data.update({'msg': 'record save fail'})
                mysql_handler.close_connection()

            else:
                logging.error("post request has no file data")
                data.update({"msg": "post request has no file data"})
        except KeyError, e:
            error = traceback.format_exc()
            data.update({'msg': "request invalid, param missing: %s" % (e)})
            logging.error(error)
        except RuntimeError, e:
            error = traceback.format_exc()
            data.update({'msg': e.message})
            logging.error(error)
        except:
            error = traceback.format_exc()
            data.update({'msg': "save file error."})
            logging.error(error)
        finally:
            if mysql_handler:
                mysql_handler.close_connection()
        result = {
            'status': status,
            'result': data
        }
        logging.info("End request, return result:{0}".format(result))
        self.wfile.write(json.dumps(result))

    @staticmethod
    def get_sub_dir_name():
        now = datetime.datetime.now()
        rel_path = '%s/%02d/%02d/' % (now.year, now.month, now.day)
        return rel_path

    @staticmethod
    def format_bytes(num):
        '''
            format bytes
        '''
        if num / 1024.0 / 1024.0 / 1024.0 > 1:
            return "%.2f" % (num / 1024.0 / 1024.0 / 1024.0) + 'GB'
        if num / 1024.0 / 1024.0 > 1:
            return "%.2f" % (num / 1024.0 / 1024.0) + 'MB'
        if num / 1024.0 > 1:
            return "%.2f" % (num / 1024.0) + 'KB'
        return "%.2f" % (num) + 'B'

class ThreadingHTTPServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer): pass


if __name__ == '__main__':
    if not path.isdir(UPLOAD_DIR):
        makedirs(UPLOAD_DIR)
        print "Folder Created: {0}".format(UPLOAD_DIR)
    server_address = (SERVER_BIND_IP, SERVER_BIND_PORT)
    httpd = ThreadingHTTPServer(server_address, WebHandler)
    try:
        logging.info("Web Server On %s:%d" % server_address)
        httpd.serve_forever()
    except KeyboardInterrupt:
        logging.info("Web Server Shutting Down...")
        httpd.shutdown()