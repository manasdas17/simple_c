int func(int a)
{
	return a + 10;
}

int main()
{
	int a = 10, b = 0;

	while(a){
	  b += 1;
	  a -= 1;
	}

	return b;
}
