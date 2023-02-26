#include <torch/script.h>
#include <torch/custom_class.h>

#include <string>
#include <vector>

template <class T> struct MyStackClass : torch::CustomClassHolder {
  std::vector<T> stack_;
  MyStackClass(std::vector<T> init) : stack_(init.begin(), init.end()) {}

  void push(T x) { stack_.push_back(x); }
  T pop() {
    auto val = stack_.back();
    stack_.pop_back();
    return val;
  }

  c10::intrusive_ptr<MyStackClass> clone() const {
    return c10::make_intrusive<MyStackClass>(stack_);
  }

  void merge(const c10::intrusive_ptr<MyStackClass> &c) {
    for (auto &elem : c->stack_) {
      push(elem);
    }
  }
};

TORCH_LIBRARY(my_classes, m) {
  m.class_<MyStackClass<std::string>>("MyStackClass")
      .def(torch::init<std::vector<std::string>>())
      .def("top",
           [](const c10::intrusive_ptr<MyStackClass<std::string>> &self) {
             return self->stack_.back();
           })
      .def("push", &MyStackClass<std::string>::push)
      .def("pop", &MyStackClass<std::string>::pop)
      .def("clone", &MyStackClass<std::string>::clone)
      .def("merge", &MyStackClass<std::string>::merge);
}
