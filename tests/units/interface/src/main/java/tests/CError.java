package tests;

public class CError implements I{

    @Override
    public Object foo() {
        return null;
    }

    public void bar(Object foo){

    }

    public void run(){
        bar(foo());
    }
}
