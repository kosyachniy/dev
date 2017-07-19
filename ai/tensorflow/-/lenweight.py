import tensorflow as tf
sess=tf.Session()

n=int(input())
m=list()
p=list()
we=list()
#d=list()
for i in range(n):
	l, w=[int(j) for j in input().split()]
	we.append(float(w))
	m.append(l/w)
	p.append(l/(w**2))
	#d.append(0.0)

x=tf.constant(we, name='input')
w=tf.Variable(p, name='weight')
y=tf.constant(m, name='right')
#b=tf.Variable(d, name='bias')

y2=tf.multiply(w, x, name='output')
#y2=tf.nn.softmax(tf.multiply(x,w)+b)

loss=tf.pow(y2-y, 2, name='loss')

print('--------------------')

sess.run(tf.global_variables_initializer())
train_step=tf.train.GradientDescentOptimizer(0.005).minimize(loss)
for i in range(100):
	sess.run(train_step)
	print(sess.run(y2))

q=int(input())
mi=abs(we[0]-q)
nom=0
for i in range(1,len(we)):
	if abs(we[i]-q)<mi:
		mi=abs(we[i]-q)
		nom=i
qw=sess.run(y2)
print(round(q*qw[nom], 0))