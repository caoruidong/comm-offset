import sys,collections
infile=open(sys.argv[1])
tree=collections.defaultdict(dict)
name={}
pipe={}
sharemem=collections.defaultdict(list)

def getformat(type):
	return {
		'clone':'',
		'pipe':'[color=red]',
		'connect':'[color=green]',
		'listen':'[color=cyan]',
		'sharemem':'[color=blue,dir=both,label=\"%s\"]',
		'msgqueue':'[color=purple]',
		'file':'[color=orchid]'
	}[type]

try:
	for line in infile:
		tmp=line.strip().split(',')
		pid=tmp[2]
		name[pid]=tmp[0]
		if 'ppid' in line: #clone
			cpid=tmp[-1].split()[0]
			if cpid[0]!='-':
				tree[pid][cpid]=getformat('clone')
			if pid in pipe:
				pipe[pid]+=[cpid]
		elif 'ffffffff812067b0' in line: #pipe
			if pid in pipe and len(pipe[pid])>1:
				c1=pipe[pid][0]
				for c2 in pipe[pid][1:]:
					tree[c1][c2]=getformat('pipe')
			pipe[pid]=[]
		elif 'ffffffff81205090' in line: #execve		
			name[pid]=tmp[-1]
		elif 'ffffffff816c8460'  in line or 'ffffffff816c8550' in line: #socket
			sfam=tmp[6][12:]
			if int(sfam,16)==2 or int(sfam,16)==10:
				saddr=tmp[6][:8]
				lisaddr=''
				for i in range(0,8,2):
					lisaddr=str(int(saddr[i:i+2],16))+'.'+lisaddr
				if lisaddr=='0.0.0.0.' or lisaddr=='10.0.2.15.' or lisaddr=='127.0.0.1.' :
					lisaddr='.'
				sport=tmp[6][8:12]
				lisport=str(int(sport[2:]+sport[:2],16))
				if 'ffffffff816c8550' in line:
					tree[pid][lisaddr[:-1]+':'+lisport]=getformat('connect')
				else: #ffffffff816c8460
					if lisport!='0':
						tree[lisaddr[:-1]+':'+lisport][pid]=getformat('listen')
		elif 'ffffffff81729920' in line: #inet_bind_hash
			lisport=tmp[-1]
			tree[lisaddr[:-1]+':'+lisport][pid]=getformat('listen')
		elif 'ffffffff81314230' in line: #shmget
			if int(tmp[-1],16)!=0:
				sharemem[tmp[-1]].append(pid)
		elif 'ffffffff8130f140' in line: #msgget
			if int(tmp[-1],16)!=0:
				tree[tmp[-1]][pid]=getformat('msgqueue')
		elif 'ffffffff811fc280' in line: #open
			if int(tmp[-1])%4!=0:
				tree[pid][tmp[5]]=getformat('file')
except Exception,e:  
    print('!!!')

for k in sharemem:
	c1=sharemem[k][0]
	for c2 in sharemem[k][1:]:
		tree[c1][c2]=getformat('sharemem')%(k)

print('digraph G {')
for s in tree:
	name0=name[s] if s in name else ''
	for e in tree[s]:
		name1=name[e] if e in name else ''
		print('\"%s %s\" -> \"%s %s\" %s'%(name0,s,name1,e,tree[s][e]))
print('}')
