/*  Modified by Daniel Wirick to serve video on tcp socket and display pixel format.
 *
 *  V4L2 video capture example, modified by Derek Molloy for the Logitech C920 camera
 *  Modifications, added the -F mode for H264 capture and associated help detail
 *  www.derekmolloy.ie
 *
 *  V4L2 video capture example
 *
 *  This program can be used and distributed without restrictions.
 *git clone git://github.com/derekmolloy/boneCV
 *      This program is provided with the V4L2 API
 * see http://linuxtv.org/docs.php for more information
 *
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

#include <getopt.h>             /* getopt_long() */

#include <fcntl.h>              /* low-level i/o */
#include <unistd.h>
#include <errno.h>
#include <arpa/inet.h>

#include <sys/stat.h>
#include <sys/types.h>
#include <sys/time.h>
#include <sys/mman.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <netinet/in.h>

#include <linux/videodev2.h>

#define CLEAR(x) memset(&(x), 0, sizeof(x))

enum io_method {
        IO_METHOD_READ,
        IO_METHOD_MMAP,
        IO_METHOD_USERPTR,
};

struct buffer {
        void   *start;
        size_t  length;
};

struct sockaddr_in myaddr;  //local net address information
struct hostent *hp;  //host information
struct sockaddr_in cli_addr; //server address

static char            *dev_name;
static enum io_method   io = IO_METHOD_MMAP;
static int              fd = -1;
static int		sd = -1;
struct buffer          *buffers;
static unsigned int     n_buffers;
static int              out_buf;
static char		*net_send;
static int              force_format = 0;
static int              frame_count = 100;
static unsigned int	clilen;
static int		clisockfd;
static unsigned int	sendbuffsize;

static void start_capturing (void);
static void stop_capturing (void);

static void debug (const char *s)
{
	fprintf (stderr, "%s", s);
}

static void print_errno (const char *s)
{
	fprintf (stderr, "%s error %d, %s\n", s, errno, strerror(errno));
}

static void errno_exit (const char *s)
{
        fprintf (stderr, "%s error %d, %s\n", s, errno, strerror(errno));
        exit(EXIT_FAILURE);
}

static int xioctl(int fh, int request, void *arg)
{
        int r;

        do {
                r = ioctl(fh, request, arg);
        } while (-1 == r && EINTR == errno);

        return r;
}

static void server_listen (void)
{
	int clients = 0;
	char introstring[100] = "This is RCOG";
	ssize_t introsize = sizeof(introstring);
	char recvintro[10];

//	struct timeval timeout;
//	timeout.tv_sec = 1;
//	timeout.tv_usec = 0;

	fprintf (stderr, "Listening for a Client Connection\n");
	//listen for incoming connections
	listen (sd, 5);

	//Verify client is looking for us
	while (clients == 0)
	{
		//Accept incoming connection
		clilen = sizeof(cli_addr);
		clisockfd = accept (sd, (struct sockaddr *) &cli_addr, &clilen);
		if (clisockfd < 0)
		{
			errno_exit("ERROR on accept");
		}
		debug("accepted connection\n");
        	/*if (setsockopt (clisockfd, SOL_SOCKET, SO_RCVTIMEO, (char *)&timeout, sizeof(timeout)) < 0)
                	print_errno("setsockopt failed\n");
			close (clisockfd);  //close the bad socket
			clisockfd = -1;

	        if (setsockopt (clisockfd, SOL_SOCKET, SO_SNDTIMEO, (char *)&timeout, sizeof(timeout)) < 0 && clisockfd > 0)
        	        print_errno("setsockopt failed\n");
			close (clisockfd);  //close the bad socket
			clisockfd = -1;*/

		if (clisockfd >= 0)
		{
			debug("sending intro message\n");
			ssize_t len = send(clisockfd, introstring, introsize, MSG_NOSIGNAL);
	                if (len < 0)
	                {
	               		print_errno ("socket send failed");
	                        close (clisockfd);  //close the bad socket
				clisockfd = -1;
	                }
		}

		if (clisockfd >= 0)
		{
			ssize_t len = recv(clisockfd, recvintro, sizeof (recvintro), 0);
			if (len < 0)
			{
	                        print_errno ("socket send failed");
	                        close (clisockfd);  //close the bad socket
				clisockfd = -1;
	                }
			debug ("Received message from client\n");
			debug (recvintro);
			if (strcmp (recvintro, "Hello RCOG") == 0)
			{
				clients = 1;
			}
		}
	}
}

//This is the server side
static void init_net (void)
{
	unsigned int m = sizeof(sendbuffsize);
	//set up data values in myaddr struct
	memset((char *)&myaddr, 0, sizeof(myaddr));
	myaddr.sin_family = AF_INET;   //Network type
	myaddr.sin_addr.s_addr = htonl(INADDR_ANY);  //Local address *important to set if more than one network interface
	myaddr.sin_port = htons(27777);  //Listen port number

	//Create a tcp socket
	if ((sd = socket(AF_INET, SOCK_STREAM, 0)) < 0)
	{
		errno_exit("cannot create socket");
		return;
	}

	//bind socket to address
	if (bind (sd, (struct sockaddr *) &myaddr, sizeof(myaddr)) < 0)
	{
		errno_exit("bind failed");
		return;
	}

	//Get the buffer size of the socket
	getsockopt(sd,SOL_SOCKET,SO_SNDBUF,(void *)&sendbuffsize, &m);
	fprintf (stderr, "Socket Send Buffer Size: %d\n", sendbuffsize);

	server_listen ();
}

static int process_image(const void *p, unsigned int size)
{
	if (net_send)
	{
		size_t sendlen = sendbuffsize;
		size_t remlen = size; //remaining length to send
		const void *curpos = p; //cursor position in data
		// send an image over tcp

		if (size < sendlen)
		{
			sendlen = size;
		}

		while (remlen > 0)
		{
			ssize_t len = send(clisockfd, curpos, sendlen, MSG_NOSIGNAL);
			if (len < 0)
			{
				print_errno ("socket send failed");
				close (clisockfd);  //close the bad socket
				stop_capturing ();
				server_listen ();
				start_capturing ();
				return (-1);
			}

			curpos += len;
			remlen -= len;
			sendlen = sendbuffsize;
			if (remlen < sendbuffsize)
			{
				sendlen = remlen;
			}
		}
	}
	else{
		fprintf (stderr, "Size of Frame: %d\n", size);

		if (out_buf)
		        fwrite(p, size, 1, stdout);  //write image out to standard out

		fflush(stderr);
		fprintf(stderr, ".");  //write a . to standard error
		fflush(stdout);
	}
	return (0);

}


//Function reads frames available for receive after select in mainloop
static int read_frame(void)
{
        struct v4l2_buffer buf;
        unsigned int i;


	//Read method if I/O is set to READ
        switch (io) {
        case IO_METHOD_READ:
                if (-1 == read(fd, buffers[0].start, buffers[0].length)) {  //performs read, if result is a fail perform following:
                        switch (errno) {
                        case EAGAIN:
                                return 0;

                        case EIO:
                                /* Could ignore EIO, see spec. */

                                /* fall through */

                        default:
                                errno_exit("read");
                        }
                }

		//Check if connection was reset
                if (-1 == process_image(buffers[0].start, buffers[0].length)) //process the read image with the process_image function
                {
                        return 0;
                }

                break;


	//memory map read method
        case IO_METHOD_MMAP:
                CLEAR(buf);

                buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
                buf.memory = V4L2_MEMORY_MMAP;

                if (-1 == xioctl(fd, VIDIOC_DQBUF, &buf)) {
                        switch (errno) {
                        case EAGAIN:
                                return 0;

                        case EIO:
                                /* Could ignore EIO, see spec. */

                                /* fall through */

                        default:
                                errno_exit("VIDIOC_DQBUF");
                        }
                }

		//checks that buf.index is less than n_buffers.  Will stop execution if false
                assert(buf.index < n_buffers);

		//See if connection was reset
                if (-1 == process_image(buffers[buf.index].start, buf.bytesused))
		{
			return 0;
		}

                if (-1 == xioctl(fd, VIDIOC_QBUF, &buf))
		{
			debug ("failed to queue read buffer");
			fprintf(stderr, "Buffer Index %d\n", buf.index);
                        errno_exit("VIDIOC_QBUF");
		}
                break;

        case IO_METHOD_USERPTR:
                CLEAR(buf);

                buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
                buf.memory = V4L2_MEMORY_USERPTR;

                if (-1 == xioctl(fd, VIDIOC_DQBUF, &buf)) {
                        switch (errno) {
                        case EAGAIN:
                                return 0;

                        case EIO:
                                /* Could ignore EIO, see spec. */

                                /* fall through */

                        default:
                                errno_exit("VIDIOC_DQBUF");
                        }
                }

                for (i = 0; i < n_buffers; ++i)
                        if (buf.m.userptr == (unsigned long)buffers[i].start
                            && buf.length == buffers[i].length)
                                break;

                assert(i < n_buffers);

		//See if connection was reset
                if (-1 == process_image((void *)buf.m.userptr, buf.bytesused))
                {
                        return 0;
                }

                if (-1 == xioctl(fd, VIDIOC_QBUF, &buf))
                        errno_exit("VIDIOC_QBUF");
                break;
        }

        return 1;
}

static void mainloop(void)
{
        unsigned int count;
	unsigned int loopIsInfinite = 0;

        if (frame_count == 0) loopIsInfinite = 1; //infinite loop
	count = frame_count;

        while ((count-- > 0) || loopIsInfinite) {
                for (;;) {
                        fd_set fds;
                        struct timeval tv;  //tv is the timeout value used below in select
                        int r;

                        FD_ZERO(&fds);
                        FD_SET(fd, &fds);

                        /* Timeout. */
                        tv.tv_sec = 2;
                        tv.tv_usec = 0;

                        r = select(fd + 1, &fds, NULL, NULL, &tv);  //fd + 1 is number of file descriptors, &fds is the file descriptor to be read

                        if (-1 == r) {
                                if (EINTR == errno)
                                        continue;
                                errno_exit("select");
                        }

                        if (0 == r) {
                                fprintf(stderr, "select timeout\n");
                                exit(EXIT_FAILURE);
                        }

                        if (read_frame())  //calls function read_frame to do the receive
                                break;
                        /* EAGAIN - continue select loop. */
                }
        }
}

static void stop_capturing(void)
{
        enum v4l2_buf_type type;
        unsigned int i;

        switch (io)
	{
        case IO_METHOD_READ:
                /* Nothing to do. */
                break;

        case IO_METHOD_MMAP: //Need to dequeue memmory buffer
                for (i = 0; i < n_buffers; ++i)
		{
                        struct v4l2_buffer buf;

                        CLEAR(buf);
                        buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
                        buf.memory = V4L2_MEMORY_MMAP;
                        buf.index = i;

                        if (-1 == xioctl(fd, VIDIOC_DQBUF, &buf))
			{
	                        switch (errno) {
	                        case EAGAIN:
	                                break;

        	                case EIO:
                	                /* Could ignore EIO, see spec. */

                        	        /* fall through */

	                        default:
        	                        errno_exit("VIDIOC_DQBUF");
                	        }
			}
		}
		//debug ("dequeued all buffers");

        case IO_METHOD_USERPTR:
		//may need to de-queue buffers here too?
                type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
                if (-1 == xioctl(fd, VIDIOC_STREAMOFF, &type))
                        errno_exit("VIDIOC_STREAMOFF");
                break;
        }
}

static void start_capturing(void)
{
        unsigned int i;
        enum v4l2_buf_type type;

        switch (io) {
        case IO_METHOD_READ:
                /* Nothing to do. */
                break;

        case IO_METHOD_MMAP:
                for (i = 0; i < n_buffers; ++i) {
                        struct v4l2_buffer buf;

                        CLEAR(buf);
                        buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
                        buf.memory = V4L2_MEMORY_MMAP;
                        buf.index = i;

                        if (-1 == xioctl(fd, VIDIOC_QBUF, &buf))
                                errno_exit("VIDIOC_QBUF");
                }
                type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
                if (-1 == xioctl(fd, VIDIOC_STREAMON, &type))
                        errno_exit("VIDIOC_STREAMON");
                break;

        case IO_METHOD_USERPTR:
                for (i = 0; i < n_buffers; ++i) {
                        struct v4l2_buffer buf;

                        CLEAR(buf);
                        buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
                        buf.memory = V4L2_MEMORY_USERPTR;
                        buf.index = i;
                        buf.m.userptr = (unsigned long)buffers[i].start;
                        buf.length = buffers[i].length;

                        if (-1 == xioctl(fd, VIDIOC_QBUF, &buf))
                                errno_exit("VIDIOC_QBUF");
                }
                type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
                if (-1 == xioctl(fd, VIDIOC_STREAMON, &type))
                        errno_exit("VIDIOC_STREAMON");
                break;
        }
}

static void uninit_device(void)
{
        unsigned int i;

        switch (io) {
        case IO_METHOD_READ:
                free(buffers[0].start);
                break;

        case IO_METHOD_MMAP:
                for (i = 0; i < n_buffers; ++i)
                        if (-1 == munmap(buffers[i].start, buffers[i].length))
                                errno_exit("munmap");
                break;

        case IO_METHOD_USERPTR:
                for (i = 0; i < n_buffers; ++i)
                        free(buffers[i].start);
                break;
        }

        free(buffers);
}

static void init_read(unsigned int buffer_size)
{
        buffers = calloc(1, sizeof(*buffers));

        if (!buffers) {
                fprintf(stderr, "Out of memory\n");
                exit(EXIT_FAILURE);
        }

        buffers[0].length = buffer_size;
        buffers[0].start = malloc(buffer_size);

        if (!buffers[0].start) {
                fprintf(stderr, "Out of memory\n");
                exit(EXIT_FAILURE);
        }
}

static void init_mmap(void)
{
        struct v4l2_requestbuffers req;

        CLEAR(req);

        req.count = 4;
        req.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        req.memory = V4L2_MEMORY_MMAP;

        if (-1 == xioctl(fd, VIDIOC_REQBUFS, &req)) {
                if (EINVAL == errno) {
                        fprintf(stderr, "%s does not support "
                                 "memory mapping\n", dev_name);
                        exit(EXIT_FAILURE);
                } else {
                        errno_exit("VIDIOC_REQBUFS");
                }
        }

        if (req.count < 2) {
                fprintf(stderr, "Insufficient buffer memory on %s\n",
                         dev_name);
                exit(EXIT_FAILURE);
        }

        buffers = calloc(req.count, sizeof(*buffers));

        if (!buffers) {
                fprintf(stderr, "Out of memory\n");
                exit(EXIT_FAILURE);
        }

        for (n_buffers = 0; n_buffers < req.count; ++n_buffers) {
                struct v4l2_buffer buf;

                CLEAR(buf);

                buf.type        = V4L2_BUF_TYPE_VIDEO_CAPTURE;
                buf.memory      = V4L2_MEMORY_MMAP;
                buf.index       = n_buffers;

                if (-1 == xioctl(fd, VIDIOC_QUERYBUF, &buf))
                        errno_exit("VIDIOC_QUERYBUF");

                buffers[n_buffers].length = buf.length;
                buffers[n_buffers].start =
                        mmap(NULL /* start anywhere */,
                              buf.length,
                              PROT_READ | PROT_WRITE /* required */,
                              MAP_SHARED /* recommended */,
                              fd, buf.m.offset);

                if (MAP_FAILED == buffers[n_buffers].start)
                        errno_exit("mmap");
        }
}

static void init_userp(unsigned int buffer_size)
{
        struct v4l2_requestbuffers req;

        CLEAR(req);

        req.count  = 4;
        req.type   = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        req.memory = V4L2_MEMORY_USERPTR;

        if (-1 == xioctl(fd, VIDIOC_REQBUFS, &req)) {
                if (EINVAL == errno) {
                        fprintf(stderr, "%s does not support "
                                 "user pointer i/o\n", dev_name);
                        exit(EXIT_FAILURE);
                } else {
                        errno_exit("VIDIOC_REQBUFS");
                }
        }

        buffers = calloc(4, sizeof(*buffers));

        if (!buffers) {
                fprintf(stderr, "Out of memory\n");
                exit(EXIT_FAILURE);
        }

        for (n_buffers = 0; n_buffers < 4; ++n_buffers) {
                buffers[n_buffers].length = buffer_size;
                buffers[n_buffers].start = malloc(buffer_size);

                if (!buffers[n_buffers].start) {
                        fprintf(stderr, "Out of memory\n");
                        exit(EXIT_FAILURE);
                }
        }
}

static void init_device(void)
{
        struct v4l2_capability cap;
        struct v4l2_cropcap cropcap;
        struct v4l2_crop crop;
        struct v4l2_format fmt;
	struct v4l2_fmtdesc fmt_desc;
	struct v4l2_streamparm strpar;
        unsigned int min;

        if (-1 == xioctl(fd, VIDIOC_QUERYCAP, &cap)) {
                if (EINVAL == errno) {
                        fprintf(stderr, "%s is no V4L2 device\n",
                                 dev_name);
                        exit(EXIT_FAILURE);
                } else {
                        errno_exit("VIDIOC_QUERYCAP");
                }
        }

        if (!(cap.capabilities & V4L2_CAP_VIDEO_CAPTURE)) {
                fprintf(stderr, "%s is no video capture device\n",
                         dev_name);
                exit(EXIT_FAILURE);
        }

        switch (io) {
        case IO_METHOD_READ:
                if (!(cap.capabilities & V4L2_CAP_READWRITE)) {
                        fprintf(stderr, "%s does not support read i/o\n",
                                 dev_name);
                        exit(EXIT_FAILURE);
                }
                break;

        case IO_METHOD_MMAP:
        case IO_METHOD_USERPTR:
                if (!(cap.capabilities & V4L2_CAP_STREAMING)) {
                        fprintf(stderr, "%s does not support streaming i/o\n",
                                 dev_name);
                        exit(EXIT_FAILURE);
                }
                break;
        }

	fmt_desc.index = 0;
	fmt_desc.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        while (0 == xioctl(fd, VIDIOC_ENUM_FMT, &fmt_desc))
	{
		fprintf(stderr, "Image Format Supported: %s\n", fmt_desc.description);
		fmt_desc.index ++;
	}


        /* Select video input, video standard and tune here. */


        CLEAR(cropcap);

        cropcap.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;

        if (0 == xioctl(fd, VIDIOC_CROPCAP, &cropcap)) {
                crop.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
                crop.c = cropcap.defrect; /* reset to default */

                if (-1 == xioctl(fd, VIDIOC_S_CROP, &crop)) {
                        switch (errno) {
                        case EINVAL:
                                /* Cropping not supported. */
                                break;
                        default:
                                /* Errors ignored. */
                                break;
                        }
                }
        } else {
                /* Errors ignored. */
        }


        CLEAR(fmt);

        fmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
	fprintf(stderr, "Force Format %d\n", force_format);
        if (force_format) {
		if (force_format==2){
             		fmt.fmt.pix.width       = 1920;
           		fmt.fmt.pix.height      = 1080;
  			fmt.fmt.pix.pixelformat = V4L2_PIX_FMT_H264;
                	fmt.fmt.pix.field       = V4L2_FIELD_INTERLACED;
		}
		else if(force_format==1){
			fmt.fmt.pix.width	= 640;
			fmt.fmt.pix.height	= 480;
			fmt.fmt.pix.pixelformat = V4L2_PIX_FMT_MJPEG;
			fmt.fmt.pix.field	= V4L2_FIELD_INTERLACED;
		}

                if (-1 == xioctl(fd, VIDIOC_S_FMT, &fmt))
                        errno_exit("VIDIOC_S_FMT");

		int a, b, c, d;
		a = fmt.fmt.pix.pixelformat & 255;
		b = (fmt.fmt.pix.pixelformat >> 8) & 255;
		c = (fmt.fmt.pix.pixelformat >> 16) & 255;
		d = (fmt.fmt.pix.pixelformat >> 24) & 255;

		fprintf(stderr, "Format set to: %c%c%c%c\n", a, b, c, d);

                /* Note VIDIOC_S_FMT may change width and height. */
        } else {
                /* Preserve original settings as set by v4l2-ctl for example */
                if (-1 == xioctl(fd, VIDIOC_G_FMT, &fmt))
                        errno_exit("VIDIOC_G_FMT");
        }

	//Set device parameters
        CLEAR(strpar);

        strpar.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;

        if (-1 == xioctl(fd, VIDIOC_G_PARM, &strpar))
		errno_exit("VIDIOC_G_PARM");

	int capability = strpar.parm.capture.capability;
	if (capability & V4L2_MODE_HIGHQUALITY)
        	fprintf(stderr, "Capture Supports High Quality Mode\n");
	if (capability & V4L2_CAP_TIMEPERFRAME)
                fprintf(stderr, "Capture Supports Time Per Frame\n");

        fprintf(stderr, "Capture Mode %d\n",strpar.parm.capture.capturemode);
        fprintf(stderr, "Capture Time Per Frame %d/%d\n",strpar.parm.capture.timeperframe.numerator, strpar.parm.capture.timeperframe.denominator);

        /* Buggy driver paranoia. */
        min = fmt.fmt.pix.width * 2;
        if (fmt.fmt.pix.bytesperline < min)
                fmt.fmt.pix.bytesperline = min;
        min = fmt.fmt.pix.bytesperline * fmt.fmt.pix.height;
        if (fmt.fmt.pix.sizeimage < min)
                fmt.fmt.pix.sizeimage = min;

        switch (io) {
        case IO_METHOD_READ:
                init_read(fmt.fmt.pix.sizeimage);
                break;

        case IO_METHOD_MMAP:
                init_mmap();
                break;

        case IO_METHOD_USERPTR:
                init_userp(fmt.fmt.pix.sizeimage);
                break;
        }
}

static void close_device(void)
{
        if (-1 == close(fd))
                errno_exit("close");

        fd = -1;
}

static void open_device(void)
{
        struct stat st;
        debug ("Opening camera device\n");
        if (-1 == stat(dev_name, &st)) {
                fprintf(stderr, "Cannot identify '%s': %d, %s\n",
                         dev_name, errno, strerror(errno));
                exit(EXIT_FAILURE);
        }

        if (!S_ISCHR(st.st_mode)) {
                fprintf(stderr, "%s is no device\n", dev_name);
                exit(EXIT_FAILURE);
        }

        fd = open(dev_name, O_RDWR /* required */ | O_NONBLOCK, 0);

        if (-1 == fd) {
                fprintf(stderr, "Cannot open '%s': %d, %s\n",
                         dev_name, errno, strerror(errno));
                exit(EXIT_FAILURE);
        }
        debug ("Finished opening camera device\n");
}

static void usage(FILE *fp, char **argv)
{
        fprintf(fp,
                 "Usage: %s [options]\n\n"
                 "Version 1.3\n"
                 "Options:\n"
                 "-d | --device name          Video device name [%s]\n"
                 "-h | --help                 Print this message\n"
                 "-m | --mmap                 Use memory mapped buffers [default]\n"
                 "-r | --read                 Use read() calls\n"
                 "-u | --userp                Use application allocated buffers\n"
                 "-o | --output               Outputs stream to stdout,"
                 "-s | --stream               Streams via TCP as server listening on port 27777"
                 "-f | --format               Force format to 640x480 MJPEG\n"//used to be YUYV
		 "-F | --formatH264           Force format to 1920x1080 H264\n"
                 "-c | --count                Number of frames to grab [%i] - use 0 for infinite\n"
                 "\n"
		 "Example usage: capture -F -o -c 300 > output.raw\n"
		 "Captures 300 frames of H264 at 1920x1080 - use raw2mpg4 script to convert to mpg4\n",
                 argv[0], dev_name, frame_count);
}

static const char short_options[] = "d:hmruosfFc:";

static const struct option
long_options[] = {
        { "device", required_argument, NULL, 'd' },
        { "help",   no_argument,       NULL, 'h' },
        { "mmap",   no_argument,       NULL, 'm' },
        { "read",   no_argument,       NULL, 'r' },
        { "userp",  no_argument,       NULL, 'u' },
        { "output", no_argument,       NULL, 'o' },
	{ "stream", no_argument,       NULL, 's' },
        { "format", no_argument,       NULL, 'f' },
	{ "formatH264", no_argument,   NULL, 'F' },
        { "count",  required_argument, NULL, 'c' },
        { 0, 0, 0, 0 }
};

int main(int argc, char **argv)
{
        dev_name = "/dev/video0";

        for (;;) {
                int idx;
                int c;

                c = getopt_long(argc, argv,
                                short_options, long_options, &idx);

                if (-1 == c)
                        break;

                switch (c) {
                case 0: /* getopt_long() flag */
                        break;

                case 'd':
                        dev_name = optarg;
                        break;

                case 'h':
                        usage(stdout, argv);
                        exit(EXIT_SUCCESS);

                case 'm':
                        io = IO_METHOD_MMAP;
                        break;

                case 'r':
                        io = IO_METHOD_READ;
                        break;

                case 'u':
                        io = IO_METHOD_USERPTR;  //user pointer I/O?
                        break;

                case 'o':
			out_buf++;
                        break;
		case 's':
			net_send++;
			init_net ();
                case 'f':
                        force_format=1;
                        break;

		case 'F':
			force_format=2;
			break;

                case 'c':
                        errno = 0;
                        frame_count = strtol(optarg, NULL, 0);
                        if (errno)
                                errno_exit(optarg);
                        break;

                default:
                        usage(stderr, argv);
                        exit(EXIT_FAILURE);
                }
        }

        open_device();
        debug ("Initializing camera device\n");
        init_device();
        debug ("Beginning capture\n");
        start_capturing();
        mainloop();
        stop_capturing();
        uninit_device();
        close_device();
	if (net_send){
		close(sd);
		close(clisockfd);
	}
        fprintf(stderr, "\n");
        return 0;
}
