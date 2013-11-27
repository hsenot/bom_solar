import os,sys,getopt
import subprocess
import psycopg2

db_name = "bom"
db_port = str(5432)
db_user = "bom"
db_password = "bom"

def main(argv):

	# Extracting parameters from command line
	inputdir = ''
	inputx = ''
	inputy = ''
	try:
		opts, args = getopt.getopt(argv,"hd:x:y:")
	except getopt.GetoptError:
		print 'txt2pg.py -d <inputdir> -x <inputlon> -y <inputlat>'
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print 'txt2pg.py -d <inputdir> -x <inputlon> -y <inputlat>'
			sys.exit()
		elif opt in ("-d"):
			inputdir = arg
		elif opt in ("-x"):
			inputx = arg
		elif opt in ("-y"):
			inputy = arg
	print 'Processing directory "', inputdir,'" at point (',inputx,',',inputy,') ...'


	fileList = []
	rootdir = inputdir
	folderCount = 0

	# Looping on all files, extracting this pixel value and pushing it into a database
	for root, subFolders, files in os.walk(rootdir):
		folderCount += len(subFolders)
		for file in files:
			fileName, fileExtension = os.path.splitext(file)
			if fileExtension == ".txt":
				f = os.path.join(root,file)
				#print(f)
				fileList.append(f)

	print 'Input directory:',len(fileList),'files in',folderCount,'directories ...'
	print str(fileList)

	# Obtaining the pixel reference to query the rasters based on the first file (fileList[0])
	# Assumption: all files have the same number of cells / cols
	pixel_output = subprocess.check_output("echo "+inputx+" "+inputy+" | gdaltransform -i -s_srs EPSG:4283 \""+fileList[0]+"\"", shell=True)
	pixel_output = pixel_output.splitlines()[0]
	pix_x, pix_y, to_discard = pixel_output.split(" ")
	print "Pixel X",pix_x
	print "Pixel Y",pix_y

	# Opening up connection to the database
	try:
		conn_str = "dbname='"+db_name+"' user='"+db_user+"' password='"+db_password+"' host='localhost' port='"+db_port+"'"
		conn = psycopg2.connect(conn_str)
		if conn:
			print "Now connected to the database "+db_name
			# Keeping only the bare minimum table: gid and geom
	except:
	    print "Unable to connect to the database"

	cur = conn.cursor()

	sql = "DROP TABLE IF EXISTS bom_pixel CASCADE"
	print sql
	cur.execute(sql)
	conn.commit()

	sql = "CREATE TABLE bom_pixel (id serial NOT NULL,x numeric(7,2),y numeric(7,2),fn text,val smallint,CONSTRAINT bom_pixel_pk PRIMARY KEY (id))"
	print sql
	cur.execute(sql)
	conn.commit()

	# Now looping on all files to get the value of this pixel across all files:
	for f in fileList:
		pixel_val = subprocess.check_output("gdallocationinfo -valonly \""+f+"\" "+pix_x+" "+pix_y, shell=True)
		f_id =  f.replace(rootdir,"").replace(" ","")
		pixel_val = pixel_val.splitlines()[0]

		sql = "insert into bom_pixel (x,y,fn,val) values ("+pix_x+","+pix_y+",'"+f_id+"',"+pixel_val+")"
		print sql
		cur.execute(sql)
		conn.commit()


if __name__ == "__main__":
	main(sys.argv[1:])




