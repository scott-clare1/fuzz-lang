fn main() {
let collection: [i32; 5] = [0, 1, 2, 3, 4];
for item in collection.iter() {
let item_squarred: i32 = item * item;
println!("{}", item_squarred);
}
}