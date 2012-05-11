int print(int * index){
	/*Assumes 0xffffffff is address mapped to cout*/
	int *console = 0xffffffff;
/*	int *index;*/
	while(*index){*console = *(index++);}
	return 1;
}

int main(){
	print("hello world\n");
	return 1;
}
