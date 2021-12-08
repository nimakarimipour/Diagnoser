package tests;
import tests.Initializer;


public abstract class B {
    protected Baz foo;

    enum Baz{
        Bar
    }

    @Initializer
    public boolean isBar() {
        return this.foo == Baz.Bar; // where Baz is an enum
    }
}

class A extends B {
    public A() {
        this.foo = Baz.Bar; // non-null expr
    }
}
