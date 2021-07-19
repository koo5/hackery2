#include <iostream>
#include <csignal>
#include <unistd.h>

using namespace std;

int *x = nullptr;
int y = 54;

void signalHandler( int signum ) {
   
   x = &y;
   cout << "Interrupt signal (" << signum << ") received.\n";
      usleep(100000);
   cout << "\n";
   
}

int main () {
   // register signal SIGINT and signal handler  

//   signal(SIGINT, signalHandler);  
   signal(SIGINT, SIG_IGN);  
   signal(SIGSEGV, signalHandler);  



   while(1) {
      cout << "Going to sleep...." << endl;
      usleep(1000000);
      cout << (int)(*x);
   }

   return 0;
}
