#!flask/bin/python
from flask import Flask, jsonify, abort, make_response, request, Response
import csv, json, pymongo, unicodedata
from pymongo import MongoClient

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, World!"

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


# generate query
def generate_query(query,min,max, name):
    if min:
        query[name] = query.get(name,{})#["$gte"]=min_price#{"$gte":min_price}
        query[name]["$gte"]=min
    if max:
        query[name] = query.get(name,{})
        query[name]["$lte"]=max

def generate_feature(lat, lng, id, prices, streetAddr, bedrooms, bathrooms, sq_ft):
    feature = {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [lng,lat]},
                    "properties": {
                        "id": id,
                        "price": prices,
                        "street": unicodedata.normalize('NFKD', streetAddr).encode('ascii','ignore'),
                        "bedrooms": bedrooms,
                        "bathrooms": bathrooms,
                        "sq_ft": sq_ft
                    }
            }
    return feature

def generate_links_header(min_price, max_price, min_bed, max_bed, min_bath, max_bath,
    pageNum, toalPageNum, num_per_page):
    if toalPageNum<=1:#if 0 page or only one page, then return nothing
        return ""
    elif pageNum==1:#first page,
        print "first page"
        result = generate_links(min_price, max_price, min_bed, max_bed, min_bath, max_bath,
    pageNum+1,num_per_page,'next')
        result += ","+generate_links(min_price, max_price, min_bed, max_bed, min_bath, max_bath,
    toalPageNum,num_per_page,'last')
    elif pageNum==toalPageNum:
        print "last page"
        result = generate_links(min_price, max_price, min_bed, max_bed, min_bath, max_bath,
    1,num_per_page,'first')
        result += ","+generate_links(min_price, max_price, min_bed, max_bed, min_bath, max_bath,
    pageNum-1,num_per_page,'prev')
    else:
        print "middle page"
        result = generate_links(min_price, max_price, min_bed, max_bed, min_bath, max_bath,
    pageNum+1,num_per_page,'next')
        result += ","+generate_links(min_price, max_price, min_bed, max_bed, min_bath, max_bath,
    toalPageNum,num_per_page,'last')
        result += generate_links(min_price, max_price, min_bed, max_bed, min_bath, max_bath,
    1,num_per_page,'first')
        result += ","+generate_links(min_price, max_price, min_bed, max_bed, min_bath, max_bath,
    pageNum-1,num_per_page,'prev')
    return result

def generate_links(min_price, max_price, min_bed, max_bed, min_bath, max_bath,
    pageNum,num_per_page , rel):
    resultString = "http://localhost:5000/listings?"
    if min_price:
        resultString+="min_price={0}".format(min_price)
    if max_price:
        resultString+="&max_price={0}".format(max_price)
    if min_bed:
        resultString+="&min_bed={0}".format(min_bed)
    if max_bed:
        resultString+="&max_bed={0}".format(max_bed)
    if min_bath:
        resultString+="&min_bath={0}".format(min_bath)
    if max_bath:
        resultString+="&max_bath={0}".format(max_bath)
    resultString+="&page={0}".format(pageNum)
    resultString+="&per_page={0}".format(num_per_page)

    return "<"+resultString+">; rel="+rel


@app.route('/listings', methods=['GET'])
def getList():
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    min_bed = request.args.get('min_bed')
    max_bed = request.args.get('max_bed')
    min_bath = request.args.get('min_bath')
    max_bath = request.args.get('max_bath')

    query = {}
    generate_query(query,min_price,max_price,'price')
    generate_query(query,min_bed,max_bed,'bedrooms')
    generate_query(query,min_bath,max_bath,'bathrooms')

    result = {
            "type": "FeatureCollection",
            "features": []
    }

    for ele in table.find(query):
        lat = float(ele['lat'])
        lng = float(ele['lng'])
        id = ele['_id']
        prices = int(ele['price'])
        streetAddr = ele['street']
        bedrooms = int(ele['bedrooms'])
        bathrooms = int(ele['bathrooms'])
        sq_ft = int(ele['sq_ft'])
        result["features"].append(generate_feature(
            lat,
            lng,
            id,
            prices,
            streetAddr,
            bedrooms,
            bathrooms,
            sq_ft
        ))
    num_per_page = int(request.args.get('per_page', 50))
    totalMatch = len(result["features"])
    print "totalMatch: {0}".format(totalMatch)
    toalPageNum = totalMatch/num_per_page
    if totalMatch%num_per_page!=0:
        toalPageNum+=1
    print "num_per_page: {0}".format(num_per_page)
    pageNum = int(request.args.get('page',1))
    print "toalPageNum: {0}".format(toalPageNum)
    print "pageNum: {0}".format(pageNum)
    if not pageNum or pageNum<=0:
        pageNum=1
    elif pageNum>toalPageNum:
        pageNum = toalPageNum
    start_index =(pageNum-1)*num_per_page
    end_index = start_index+num_per_page-1
    if end_index>=totalMatch:
        end_index = totalMatch-1
    result["features"] = result["features"][start_index:end_index+1]
    result_string = json.dumps(result)
    #with open("result","w") as resultfile:
    #    json.dump(result,resultfile)
    resp = Response(result_string, status=200, mimetype='application/json')
    link_header = generate_links_header(min_price, max_price, min_bed, max_bed, min_bath, max_bath
                                       , pageNum, toalPageNum, num_per_page)
    #print "link_header: "+link_header
    resp.headers['Link'] = link_header
    #return json.dumps(result)
    return resp

def csvToJson(inputfilepath,table):
    with open(inputfilepath,'r') as csvFile:
        csvDict = csv.DictReader( csvFile, restkey=None, restval=None, )
        for obj in csvDict:
            obj['_id']= int(obj['id'])
            del obj['id']
            table.insert_one(obj)

def clean():
    client.close()

if __name__ == '__main__':
    #client = MongoClient('localhost', 27017)
    client = MongoClient()
    #client.database_names() get a list of the name of the database
    #client.close() to close the connection to mongodb
    if 'house_database' in client.database_names():
        #should delete this database 
        client.drop_database('house_database')
    #create this database
    db = client.house_database
    # db.collection_names(): listing all of the collections in our database
    #then create a collection
    table = db.house_table
    # table.find() --find() returns a Cursor instance, which allows us to iterate over all matching documents
    #parse json object from csv document, and then insert json object into database table
    csvToJson("listings.csv", table)
    
    #run server
    app.run(debug=True)
    print "close connection to mongodb"
    client.close()

