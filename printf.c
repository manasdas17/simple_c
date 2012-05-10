int write(int* string){
    int *console = 0xffffffff;
    int *p = string;
    while(*p){
        *console = *p;
        p = p + 1;
    }
    return 1;
}

int main(){
	write("abc\n");
	return 1;
}
