import os
import paho.mqtt.client as paho

#topic = "/sensores/F313CFA8"
#message = "{\"Tipo\":\"Dato\",\"ID\":\"40D88C3E\",\"v1\":\"1\",\"v2\":\"2\",\"v3\":\"3\",\"c1\":\"1\",\"c2\":\"2\",\"c3\":\"3\"}"

class Publisher:

	user = "htech"
	#broker = "157.230.218.225"
	broker = "htech.mx"
	#port = 1883
	port = 8883

	def publicar(self,topic,message,password):
		client = paho.Client()
		client.username_pw_set(username = self.user ,password = password)
		client.tls_set('%s/.sigrdap/ca_certificate/ca.crt' % os.path.expanduser('~'))
		#client.on_publish = on_publish
		client.connect(self.broker,self.port)
		ret = client.publish(topic,message, qos = 1, retain = False)
		#print(message)
		#print ("Data published")
		#print (ret)
		client.disconnect()
