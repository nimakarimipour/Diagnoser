package tests;
import tests.Initializer;


public abstract class Main {
    protected Baz foo;

    enum Baz{
        Bar
    }

    
    @Initializer
    public boolean isBar() {
        return this.foo == Baz.Bar; // where Baz is an enum
    }
}

class A extends Main {
    public A() {
        this.foo = Baz.Bar;
    }
}