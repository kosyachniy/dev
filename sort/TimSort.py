import timeit
start=timeit.default_timer()

a=[1,5,7,3,6,6,2566,774,2,0,0,0,-3]
a.sort()
print(a)

print(timeit.default_timer()-start)