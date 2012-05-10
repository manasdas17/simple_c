int main(){
	int *console = 0xffffffff;
	int *a;
	a = "abcdef\n";
	while(*a){*console = *(a++);}
	return a;
}
