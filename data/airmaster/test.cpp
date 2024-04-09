#include <iostream>
#include <fcntl.h>
#include <termios.h>
#include <unistd.h>
#include <iomanip>
#include <mosquitto.h>


int serialPortFd;
struct mosquitto *mosq = 0;


void puttt(std::string name, const std::string value)
{
	if (!mosq)
		return;
	std::string topic = "am7/sensor/" + name + "/state";
    int ret = mosquitto_publish(mosq, NULL, topic.c_str(), 7, "value.c_str()", 0, false);
    if(ret){
        std::cerr << "Can't publish to topic " << topic << std::endl;
    }   
}


bool setup() {
    const char* serialPort = std::getenv("AM7_PORT");
	if (!serialPort) {
		std::cerr << "AM7_PORT not set, using /dev/ttyUSB0" << std::endl;
		serialPort = "/dev/ttyUSB0";
	}

    serialPortFd = open(serialPort, O_RDWR | O_NOCTTY | O_NONBLOCK);
    if (serialPortFd == -1) {
        std::cerr << "Error opening serial port" << std::endl;
        return false;
    }

    // Configure serial port
    const int baudRate = B19200;
    struct termios options;
    tcgetattr(serialPortFd, &options);
    cfsetispeed(&options, baudRate);
    cfsetospeed(&options, baudRate);
    options.c_cflag |= (CLOCAL | CREAD);
    options.c_cflag &= ~PARENB;
    options.c_cflag &= ~CSTOPB;
    options.c_cflag &= ~CSIZE;
    options.c_cflag |= CS8;
    options.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG);
    options.c_oflag &= ~OPOST;
    tcsetattr(serialPortFd, TCSANOW, &options);
    std::cout << "Serial communication initialized." << std::endl;
   

    mosquitto_lib_init();
    
    
    mosq = mosquitto_new(NULL, true, NULL);
    if(!mosq){
        std::cout << "Can't initialize Mosquitto library\n";
    }
    
    const char* mqtt_host_cstr = std::getenv("MQTT_HOST");
	if (!mqtt_host_cstr) {
    	std::cout << "MQTT_HOST environment variable not set\n";
	}
	else
	{
		std::string host(mqtt_host_cstr);
	
		int mqtt_port = 1883;

		const char* mqtt_port_str = std::getenv("MQTT_PORT");
		if (mqtt_port_str) {
			mqtt_port = atoi(mqtt_port_str);
		}
    
		int ret = mosquitto_connect(mosq, host.c_str(), mqtt_port, 60);
		if(ret){
			std::cout << "Can't connect to " << host << std::endl;
			mosq = 0;
		}
	}

	puttt("hello", "world");
    return true;
}


void loop() {
    // Send command to the sensor
    
    unsigned char command[] = {0x55, 0xCD, 0x47, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x69, 0x0D, 0x0A};
    write(serialPortFd, command, sizeof(command));

    usleep(1 * 1000 * 1000);

    // Read data from the sensor
    unsigned char buffer[40];
    int bytesRead = read(serialPortFd, buffer, sizeof(buffer));
    bool alrighty = false;
    if (bytesRead == 40) {
		std::cout << "40 Data received." << std::endl;
		std::cout << std::endl;
		
        // Process the data
        unsigned int pm25 = buffer[2] | buffer[1] << 8;
        unsigned int pm10 = buffer[4] | buffer[3] << 8;
        double hcho = (buffer[6] | buffer[5] << 8) / 1000.0;
        double tvoc = (buffer[8] | buffer[7] << 8) / 1000.0;
        unsigned int co2 = buffer[10] | buffer[9] << 8;
        
        double temp = (buffer[12] | buffer[11] << 8) / 100.0;
        double humidity = (buffer[14] | buffer[13] << 8) / 100.0;

        unsigned int ppm03 = buffer[20] | buffer[19] << 8;
        unsigned int ppm05 = buffer[22] | buffer[21] << 8;
        unsigned int ppm1 = buffer[24] | buffer[23] << 8;
        unsigned int ppm2 = buffer[26] | buffer[25] << 8;
        unsigned int ppm5 = buffer[28] | buffer[27] << 8;
        unsigned int ppm10 = buffer[30] | buffer[29] << 8;

        unsigned int check = buffer[37] | buffer[36] << 8;
        unsigned int sum = 0;

        for (int i = 0; i < 36; i++) {
            sum += buffer[i];
        }

        if (check == sum && check != 0) {
            
            std::cout << "PM2.5: " << pm25 << " ug/m3" << std::endl;            
            std::cout << "PM10: " << pm10 << " ug/m3" << std::endl;
            std::cout << "HCHO: " << hcho << " ug/m3" << std::endl;
            std::cout << "TVOC: " << tvoc << " ug/m3" << std::endl;
            std::cout << "CO2: " << co2 << " ppm" << std::endl;
            std::cout << "Temp: " << temp << " °C" << std::endl;
            std::cout << "Hum: " << humidity << " %" << std::endl;
            std::cout << "PM0.3: " << ppm03 << " ppm" << std::endl;
            std::cout << "PM0.5: " << ppm05 << " ppm" << std::endl;
            std::cout << "PM1.0: " << ppm1 << " ppm" << std::endl;
            std::cout << "PM2.5: " << ppm2 << " ppm" << std::endl;
            std::cout << "PM5.0: " << ppm5 << " ppm" << std::endl;
            std::cout << "PM10: " << ppm10 << " ppm" << std::endl;
            
            std::cout << std::endl;
            alrighty = true;

        } else {
            std::cout << "checksum error." << std::endl;
        }
        
    } else {
        std::cerr << "Error, bytesRead != 40: " << bytesRead << std::endl;
    }
	
	if (!alrighty)
	{
		std::cerr << "bytesRead: " << static_cast<int>(bytesRead)  << ". Data: ";
		for (int i = 0; i < bytesRead; i++) {
        	std::cerr << std::hex << std::setw(3) << std::setfill('0') << static_cast<int>(buffer[i]) << " ";
        	if (i == 39)
        		break;
    	}
    	std::cerr << std::endl;	
	}

}

int main() {
    
    if (setup())
    {
		while (true) {
			loop();
		}
	}
	    
	if (mosq)
	{
		mosquitto_disconnect(mosq);
		mosquitto_destroy(mosq);
		mosquitto_lib_cleanup();
	}    
    
    return 0;
}
