public class Car{
    private Engine engine = new Engine();
    private Airplane noway;

    public static void main(String args[]){
     String model = "Hello Java";
     String dead = "dead";
     System.out.println(model);
    }

    public void Run(String args[]){
     String text = "Hello Java";
     int number = 5 + 10;
     System.out.println(text);
    }
    public void Fly(String args[]){
        return;
    }
    public void Drive(String args, int wheels){
        this.engine.SetName("Yamaha", "last");
    }
}

class Airplane{
    private Engine engine = new Engine();
    private String brand;

    public static void main(String args[]){
     String text = "Hello Java";
     int deadVariable = 10 - 8;
     System.out.println(text);
    }
    public void Fly(String args[]){
        System.out.println("FLy");
    }
    public void Checkup(String args[]){

    }
}

class Engine{
    public String Name;
    private String model;

    public static void main(String args[], int k){
     String text = "Hello Java";
     System.out.println(text);
    }
    public void SetName(String X, String last){
        Car what = new Car();
        this.Name = X;
    }
    public void main2(String args[]){
     String text = "Hello Java";
     String variable;
     String dead = "";
     System.out.println(text);
    }

}