# Welcome to my GitHub 😼
* Hi there, I'm Jake! 👨‍🦱
* Currently studying Computer Science at UBC 💻
* Living in Vancouver, BC 🇨🇦
* Originally from Bristol, England 🇬🇧

# A little bit about me... 😎
```java
public class Jake {
    private String name;
    private int age;
    private List<String> hobbies;

    public Jake() {
        this.name = "Jake Gaunt";
        this.age = 19;
        this.hobbies = Arrays.asList("Swimming", "Video Games", "Skiing");
    }

    public void introduceMyself() {
        System.out.println("Hello World! My name is " + name);
        System.out.println("I am currently a " + age + " years old ");
        System.out.println("My hobbies are: ");
        hobbies.forEach(System.out::println);
    }

    public static void main(String[] args) {
        new Jake().introduceMyself();
    }
}
```

```bash
$ javac Jake.java
$ java Jake
```
```plaintext
Hello World! My name is Jake Gaunt
I am currently a 19 years old 
My hobbies are: 
Swimming
Video Games
Skiing

```

# Statistics

<div style="display: flex; justify-content: space-between; align-items: center;">

  <img src="https://github-readme-stats.vercel.app/api/?username=jx4e&count_private=true&theme=tokyonight&showicons=true" alt="My GitHub Stats" style="width: 49%; height: 200px;"/>

  <img src="https://github-readme-stats.vercel.app/api/top-langs/?username=jx4e&langs_count=5&theme=tokyonight" alt="My GitHub Language Stats" style="width: 49%; height: 200px;"/>

</div>
