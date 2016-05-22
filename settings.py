from pymongo import MongoClient
import getopt,sys
baseUrl = 'http://www.hospitalitynet.org'
host = 'localhost'
port = 27017
db_name = 'test'
collections = {'brand': 'brands', 'organization': 'organizations'}
client = None


def init():
    global client, host, port, db_name, collections
    repair = False
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h:p:d:b:o:r", ["host=", "port=", "db_name=", "brand_col=", "org_col=", "repair="])
    except getopt.GetoptError:
        print('Usage: %s [-h <hostname>] [-p <port>] [-d <db_name>] [-b <brand_coll>] [-o <org_coll>]' % sys.argv[0])
        sys.exit(2)


    for opt, arg in opts:
        if opt in ('-h', "--host"):
            host = arg
        elif opt in ("-p", "--port"):
            port = arg
        elif opt in ("-d", "--db"):
            db_name = arg
        elif opt in ("-b", "--brand_col"):
            collections['brand'] = arg
        elif opt in ("-o", "--org_col"):
            collections['organization'] = arg
        elif opt in ("-r", "--repair"):
            repair = True

    client = MongoClient(host, port)
    return repair


def destroy():
    client.close()
