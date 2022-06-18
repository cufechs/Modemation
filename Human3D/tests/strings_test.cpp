#include <iostream>
#include <string>
#include <vector>
#include <json/json.hpp>
#include <fstream>

int main() {

    

    std::string male_dir = "/Users/abdelrahmanabdelghany/Documents/college/semester10/GP/Human3D/data/male/01.json";
    std::size_t p = male_dir.find_last_of('/');
    std::cout << "p: " << p << "\n";
    std::string s = male_dir.substr(p+1);
    std::cout << "substring: " << s << "\n";
    
    std::vector<std::string> v{"aa/bb/01.obj", "aa/bb/01.json", 
        "aa/bb/03.obj", "aa/bb/02.json",
        "aa/bb/02.obj", "aa/bb/03.json"};

    
    for (const auto& s: v ) {
        std::size_t start_index = s.find_last_of('/')+1;
        std::size_t last_index = s.find(".json");
        std::cout << "last_index: " << last_index << "\n";
        std::cout << s.substr(start_index, last_index-start_index) << "\n";
    }
    
    std::ifstream json_file("/Users/abdelrahmanabdelghany/Documents/college/semester10/GP/Human3D/data/male/1_human.json");
    nlohmann::json json;
    json_file >> json;
    json_file.close();

    std::cout << "json[gender]: " << json["gender"] << "\n";
    std::cout << "json[height]: " << json["height"] << "\n";
    std::cout << "json[weight]: " << json["weight"] << "\n";

    // std::string test_str = "/aa/bb/cc.json";
    // std::string delim = ".json";
    // std::size_t pos = test_str.find(delim);
    // std::cout << "pos: " << pos << "\n";
    // if (pos >= 0 && pos < test_str.size()) {
    //     std::string s = test_str.substr(pos);
    //     std::cout << "s: " << s << "\n";
    //     std::cout << "splitted: " << s << std::endl;
    // } else {
    //     std::cout << "nothing found\n";
    // }

    return 0;
}