#include <iostream>
#include <string>
#include <vector>
#include <sstream>
#include <cassert>

// #define DEBUG

#ifdef DEBUG
#define debug(s) std::cout << s << std::endl
#else
#define debug(s) {}
#endif

enum TokenType {
    NONE,
    INCP,
    DECP,
    INCN,
    DECN,
    OUT,
    IN,
    JZ,
    JNZ
};

std::string repr(TokenType token) {
    switch(token) {
        case (INCP):{
            return "INCP";
        }
        case (DECP):{
            return "DECP";
        }
        case (INCN):{
            return "INCN";
        }
        case (DECN):{
            return "DECN";
        }
        case (OUT):{
            return "OUT";
        }
        case (IN):{
            return "IN";
        }
        case (JZ):{
            return "JZ";
        }
        case (JNZ):{
            return "JNZ";
        }
        case (NONE):{
            return "NONE";
        }
    }
}

std::vector<TokenType> tokenizer(std::string code) {
    std::vector<TokenType> tokens = {};
    for(char c : code) {
        debug("parsing token " << c);
        switch(c) {
            case ('>'):{
                tokens.push_back(INCP);
                break;
            }
            case ('<'):{
                tokens.push_back(DECP);
                break;
            }
            case ('+'):{
                tokens.push_back(INCN);
                break;
            }
            case ('-'):{
                tokens.push_back(DECN);
                break;
            }
            case ('.'):{
                tokens.push_back(OUT);
                break;
            }
            case (','):{
                tokens.push_back(IN);
                break;
            }
            case ('['):{
                tokens.push_back(JZ);
                break;
            }
            case (']'):{
                tokens.push_back(JNZ);
                break;
            }
            default: {
                throw "Invalid syntax";
            }
        }
    }
    return tokens;
}



class Interpreter {
public:
    std::ostringstream out;
    Interpreter(std::string code, std::string input) {
        debug("initializing interpreter with " << code << " and " << input);
        this->code = code;
        this->input = input;
        this->tokens = tokenizer(code);
        this->data = {};
        this->out = std::ostringstream();
        debug("end initialization");
    };
    // for error codes
    int run() {
        int di = 0; // data index
        int ti = 0; // token index
        int ii = 0; // input index
        TokenType token;
        for(;;) {
            debug("start of run loop");
            token = consume(ti);
            switch(token) {
                case (INCP):{
                    debug(repr(INCP));
                    di++;
                    if (di == this->data.size()) {
                        this->data.push_back(static_cast<char>(0));
                    }
                    break;
                }
                case (DECP):{
                    debug(repr(DECP));
                    di--;
                    if (di == -1) {
                        this->data.emplace(this->data.begin(), static_cast<char>(0));
                        di++;
                    }
                    break;
                }
                case (INCN):{
                    debug(repr(INCN));
                    ensureSpace(di);
                    if (this->data[di] == static_cast<char>(255)) {
                        this->data[di] = 0;
                    } else {
                        this->data[di]++;
                    }
                    break;
                }
                case (DECN):{
                    debug(repr(DECN));
                    ensureSpace(di);
                    if (this->data[di] == static_cast<char>(0)) {
                        this->data[di] = 255;
                    } else {
                        this->data[di]--;
                    }
                    break;
                }
                case (OUT):{
                    debug(repr(OUT));
                    ensureSpace(di);
                    std::cout << this->data[di];
                    out << this->data[di];
                    break;
                }
                case (IN):{
                    ensureSpace(di);
                    debug("consuming input at idx " << ii << " which is " << input[ii]);
                    debug("di is " << di << " and ti is " << ti);
                    debug("int value of input[ii] is " << static_cast<int>(input[ii]));
                    this->data[di] = input[ii];
                    debug("put input char in data array");
                    ii++;
                    debug("incremented pointer");
                    break;
                }
                case (JZ):{
                    debug(repr(JZ));
                    if (this->data[di] == 0) {
                        // by passing ti we give enough information to get the matching bracket
                        int error = jumpforward(ti);
                        if (error != 0) {
                            debug("di = " << di << " and ii = " << ii << " and ti = " << ti);
                            return error;
                        }
                    }
                    break;
                }
                case (JNZ):{
                    debug(repr(JNZ));
                    if (this->data[di] != 0) {
                        // by passing ti we give enough information to get the matching bracket
                        int error = jumpback(ti);
                        if (error != 0) {
                            debug("di = " << di << " and ii = " << ii << " and ti = " << ti);
                            return error;
                        }
                    }
                    break;
                }
                case (NONE):{
                    return 0;
                }
                default: {
                    debug("syntax error? " << this->tokens[ti]);
                    return -1;
                }
            }
            debug("end of run loop");
        }
    }
private:
    std::vector<TokenType> tokens;
    std::string input;
    std::vector<char> data;
    std::string code;
    TokenType consume(int& i) {
        // returns token at that current indext then increments instruction index
        debug("consuming token at " << i << " which is " << repr(this->tokens[i]));
        if (i == this->tokens.size()) {
            return NONE;
        }
        i++; // increment token count and return token
        return this->tokens[i-1];
    }
    int jumpforward(int& i){
        debug("jumping forward");
        int begin = i;
        i--; // to counteract the auto i++ in consume
        // i is the current position in the token list
        // this function only gets called when actually jumping forward
        if (tokens[i] != JZ) {
            debug("this error should never happen as jumpforward is only called when tokens[i] = JZ");
            debug("i = " << i << " and was " << i+1);
            return -1; // indicate error
        }
        // bracket matching done through iteration
        // start with a 1, and move the index forward
        // iterate till ct == 0
        int ct = 1;
        i++;
        for(TokenType t = tokens[i]; i < tokens.size() && ct != 0; t = tokens[++i]) {
            if (t == JZ) {
                ct++; // additional JZ adds 1
            } else if (t == JNZ) {
                ct--; // matching JNZ subs 1
            }
        }
        i--;
        if (ct != 0 || tokens[i] != JNZ) {
            debug("ct = " << ct << " and tokens near i are = [" << repr(tokens[i-1]) << ", " << repr(tokens[i]) << ", " << repr(tokens[i+1]) << "] and i = " << i);
            debug("erronious code string seems to be " << this->code.substr(begin-1, 1+i-begin));
            return -1; // indicate error
        }
        //postcondition asserted, ct == 0 and tokens[i] == JNZ
        i++; // to move instruction pointer past the matching bracket
        return 0;
    }
    int jumpback(int& i){
        debug("jumping backward");
        i--; // to counteract the auto i++ in consume
        // i is the current position in the token list
        // this function only gets called when actually jumping forward
        debug("i = " << i << " and token = " << repr(tokens[i]));
        if (tokens[i] != JNZ) {
            return -1; // indicate error
        }
        // bracket matching done through iteration
        // start with a 1, and move the index forward
        // iterate till ct == 0
        int ct = 1;
        i--;
        for(TokenType t = tokens[i]; i >= 0 && ct != 0; t = tokens[--i]) {
            if (t == JZ) {
                ct--;
            } else if (t == JNZ) {
                ct++;
            }
        }
        i++; // to move instruction pointer past the matching bracket???
        debug("i = " << i << " ct = " << ct << " and token = " << repr(tokens[i]));
        if (ct != 0 || tokens[i] != JZ) {
            return -1; // indicate error
        }
        i++; // to actually move the instruction pointer past the matching bracket
        //postcondition asserted, ct == 0 and tokens[i] == JZ
        debug("i = " << i);
        return 0;
    }
    void ensureSpace(int di){
        if (this->data.size() <= di) {
            this->data.resize(di+1);
        }
    }
};

std::string brainLuck(std::string code, std::string input) {
    auto interpreter = new Interpreter(code, input);
    int error = interpreter->run();
    if (error != 0) {
        return "error happened";
    }
    std::cout << "interpreter output" << std::endl;
    std::cout << interpreter->out.str() << std::endl;
    return interpreter->out.str();
}

// int main(int argc, char const *argv[]) {
//     if (argc == 1) {
//         // std::vector<char> chararray = {};
//         // chararray.push_back(0);
//         // chararray[0] = 99;
//         // std::cout << chararray[0] << std::endl;

//         // //echo until "255"
//         // std::string tw = "codewars";
//         // tw.append(1,(char)255);
//         // assert(brainCluck(",+[-.,+]",tw) == "codewars");

//         // //echo until "0";
//         // std::string mw = "codewars";
//         // mw.append(1,(char)0);
//         // assert(brainCluck(",[.[-],]",mw) == "codewars");

//         std::string dw;
//         dw.append(1, (char) 7);
//         dw.append(1, (char) 3);
//         std::string result;
//         result.append(1, (char)21);
//         auto actual = brainLuck(",>,<[>[->+>+<<]>>[-<<+>>]<<<-]>>.",dw);
//         std::cout << static_cast<int>(actual[0]) << std::endl;
//     } else {
//         std::string code = static_cast<std::string>(argv[1]);
//         std::string input;
//         if (argc > 2) {
//             input = static_cast<std::string>(argv[2]);
//         } else {
//             input = "";
//         }
//         auto interpreter = new Interpreter(code, input);
//         int error = interpreter->run();
//         if (error != 0) {
//             std::cout << "error happened" << std::endl;
//             return -1;
//         }
//         std::cout << "interpreter output" << std::endl;
//         std::cout << interpreter->out.str() << std::endl;
//         return 0;
//     }
// }
