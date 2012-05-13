int print_string(int * index){
	/*Assumes 0xffffffff is address mapped to cout*/
	int *console = 0xffffffff;
	while(*index){*console = *(index++);}
	return 1;
}

int print_int(int i){
	int decade;
	int digit;
	int *console = 0xffffffff;
	int leading = 1;

	for(decade = 1000000000; decade; decade /= 10){
		for(digit=0; i >= decade; i-=decade) digit++;
		*console = digit + '0';
	}
}

int main(){
	print_string("hello world\n");
	print_int(130);
	return 1;
}
