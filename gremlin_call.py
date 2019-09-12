
from gremlin_python.driver import client, serializer

# database，graph，クエリを指定して，発行しcallbackを取得
def call_gremlin(database='',graph="",key="",query=""):
    ENDPOINT = ''
    c = client.Client(ENDPOINT, 'g',
                      username="/dbs/{0}/colls/{1}".format(
                          database, graph),
                      password="{}".format(key),
                      message_serializer=serializer.GraphSONSerializersV2d0()
                      )
    # クエリを発行してcallbackを取得
    callback = c.submitAsync(query)
    # コールバックが複数回に分かれて返ってくるので一つのリストにする
    response = [res for result in callback.result() for res in result]
    return response

if __name__ == "__main__":
    # test
    print(call_gremlin(query = "g.V().hasLabel('group').has('fullName','').in('belongsTo').values('name')"))
    
