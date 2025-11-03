// this is a minimal implementation to allow MCAP to compile without C++17
#include <string>

namespace mcap14 {

// Minimal byte type (alias for unsigned char)
typedef unsigned char byte;

// Minimal optional implementation (pointer-based, for POD types!)
template< typename T >
class optional
{
    bool has_val;
    T value;

public:
    optional()
        : has_val( false )
    {
    }
    optional( const T & v )
        : has_val( true )
        , value( v )
    {
    }
    bool has_value() const { return has_val; }
    operator bool() const { return has_val; }
    T & operator*() { return value; }
    const T & operator*() const { return value; }
    T * operator->() { return &value; }
    const T * operator->() const { return &value; }
};

// Minimal string_view (pointer + size - for read-only use)
class string_view
{
    const char * data_;
    size_t size_;

public:
    string_view()
        : data_( nullptr )
        , size_( 0 )
    {
    }
    string_view( const char * s, size_t n )
        : data_( s )
        , size_( n )
    {
    }
    string_view( const std::string & s )
        : data_( s.data() )
        , size_( s.size() )
    {
    }
    string_view( const char * s )
        : data_( s )
        , size_( s ? strlen( s ) : 0 )
    {
    }

    const char * data() const { return data_; }
    size_t size() const { return size_; }
    bool empty() const { return size_ == 0; }
    const char * begin() const { return data_; }
    const char * end() const { return data_ + size_; }

    // Conversion to std::string
    operator std::string() const { return std::string( data_, size_ ); }
};
}  // namespace mcap14

// Optionally, include MCAP headers here if they require the types
#include <mcap/writer.hpp>
#include <mcap/reader.hpp>
#define MCAP_IMPLEMENTATION
