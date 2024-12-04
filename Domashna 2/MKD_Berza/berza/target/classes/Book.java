import jakarta.persistence.*;
import jakarta.persistence.Entity;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.Generated;
import lombok.NoArgsConstructor;

import java.io.Serializable;


@Data
@Entity
@Table(name = "books")
@NoArgsConstructor
@AllArgsConstructor
public class Book implements Serializable {

    /**
     *
     */
    private static final long serialVersionUID = 898002081458478671L;
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @NotNull(message = "Book must have a title")
    @Column(unique = true)
    private String bookName;
    @NotEmpty(message = "Author must not be empty")
    private String author;
    @Positive(message = "Price value must be greater than zero")
    private Integer price;
    private Boolean isInStock;

}
