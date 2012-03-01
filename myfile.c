int mul(int a, int b){
  return a*b;
}

int func(int a, int b){
  return mul(a+1, b+1);
}

int afunc(int a, int b){
  return func(a+1, b+1);
}

int main()
{
    int a = 10;
    int b = 0;

    while(a){
      a = a - 1;
      b = b + 1;
    }
	
    return b;
}
