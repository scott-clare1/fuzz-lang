fn sum_of_first_n_natural_numbers(n: i32) -> i32 {
let n_plus_one: i32 = n + 1;
let n_product: i32 = n * n_plus_one;
let sum: i32 = n_product / 2;
return sum;}
fn square(a: f32) -> f32 {
let x: f32 = a * a;
return x;}
fn main() {
let collection: [i32; 5] = [0, 1, 2, 3, 4];
for item in collection.iter() {
println!("{}", item);
}
let x: f32 = square(10.1);
let y: &str = "scott";
let sum_of_first_ten_natural_numbers: i32 = sum_of_first_n_natural_numbers(10);
println!("{}", x);
println!("{}", y);
println!("{}", sum_of_first_ten_natural_numbers);
}
