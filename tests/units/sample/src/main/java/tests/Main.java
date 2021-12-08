package tests;

public abstract class Main {
    protected Baz foo;

    enum Baz{
        Bar
    }

    
    public boolean isBar() {
        return this.foo == Baz.Bar; // where Baz is an enum
    }
}

class A extends Main {
    public A() {
        this.foo = Baz.Bar;
    }
}